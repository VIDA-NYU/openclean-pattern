from openclean import NEW_HYPHEN_SYMBOL, GAP_SYMBOL

from openclean.tokenize.factory import TokenizerFactory
from openclean.tokenize import TOKENIZER_REGEX

from openclean.align.factory import AlignerFactory
from openclean.align import ALIGNER_COMB
from openclean.align.distance import DISTANCE_TDE, DISTANCE_ETDE

from openclean.regex.compiler import RegexCompiler
from openclean.evaluate import Evaluator

import numpy as np, pandas as pd, re, os, operator, warnings

from typing import Union, List, Dict

os.chdir(os.path.abspath(os.path.dirname(__file__)))

class PatternFinder(object):
    '''
    PatternFinder class that users will use to identify patterns and anomalies
    '''
    def __init__(self, series: Union[Dict, List],
                 frac: float = 1,
                 tokenizer: str = TOKENIZER_REGEX,
                 aligner: Union[str, None] = ALIGNER_COMB,
                 distance: str = DISTANCE_TDE) -> None:
        '''
        Initialize the pattern finder object. This assumes that the input columns have been sampled if too large

        :param series: list of column values or dict of column values:frequency
        :type series: list or dict
        :param frac: sample size
        :type frac: float
        :param tokenizer: the tokenizer to use
        :type tokenizer: str
        :param aligner: the aligner to use
        :type aligner: str
        :param distance: distance to use for clustering
        :type distance: string
        '''
        self.series = self._sample(series, frac)
        self._tokenizer = TokenizerFactory(tokenizer).get_tokenizer()
        self._distance = distance
        self._aligner = AlignerFactory(aligner, distance).get_aligner() # default is naive-all-combinations-aligner
        self._distance_array = None
        self._aligned = None
        self.clusters = None
        self.regex = None
        self.outliers = dict()


    def _sample(self, series, frac):
        '''
        randomly samples large columns and resolve frequency
        :param series: list of column values or dict of column values:frequency
        :type series: list or dict
        :param frac: distance to use for clustering
        :type frac: int
        :return: pandas DataFrame
        '''
        if isinstance(series, dict):
            df = pd.DataFrame.from_dict(series, orient='index').reset_index()
            df.columns = ['column', 'freq']
            df['column'] = df['column'].astype('str').str.lower()
        elif isinstance(series, list):
            df = pd.DataFrame(series).dropna().reset_index(drop=True).astype('str')
            df = df[0].str.lower().value_counts().reset_index()
            df.columns = ['column','freq']
        else:
            raise ValueError("Input column not valid")

        df['column'] = df['column'].str.replace('\'', '')
        return df.sample(frac=frac, random_state=42).reset_index() # for now, remove apostrophes

    def _align(self, tokens):
        '''
        align - memoized. Default alignment is the light weight version which only aggregates by # of tokens
        :param tokens: list of tokenized column values
        :type tokens: pd.Series
        :return: numpy array / df
        '''
        if self._aligned is None:
            if self._aligner is not None:
                aligned = self._aligner.get_aligned(tokens.tolist())  # todo: fix lingpy to return df:[tokens,cluster] not np array
            else:
                aligned = pd.DataFrame(tokens)
                aligned['cluster'] = tokens.apply(len)
                aligned['aligned'] = tokens

            aligned['pre_align_tokens'] = tokens
            aligned['len'] = aligned['aligned'].str.len()

            self._aligned = aligned
        return self._aligned

    def encode_and_find(self):
        if self._distance != DISTANCE_ETDE:
            raise ValueError("To encode, initialize pattern finder with distance='ETDE'")
        pat_column = 'encoded_tokens'

        series = self.series
        tokenizer = self._tokenizer

        freq = series.groupby('column').agg('freq').sum().to_dict()
        # convert all rows to internally represented objects
        series[pat_column], _ = tokenizer.encode(series['column'], freq)
        aligned = self._align(series[pat_column])
        if pat_column in aligned:
            aligned = aligned.drop(pat_column, 1)

        aligned_series = series.merge(aligned, left_on='encoded_tokens', right_on='pre_align_tokens')
        self.clusters = aligned_series[['column','cluster']]

        proportion = dict(aligned_series.groupby('cluster').agg('freq').sum() / aligned_series.freq.sum())
        column_length = aligned_series.freq.sum()

        results = dict()
        generalized = dict()
        sample = dict()
        for cluster in aligned_series['cluster'].unique():
            if cluster == -1:
                continue # -1 is the noise cluster with anything that did not align

            this_cluster = aligned_series[aligned_series['cluster'] == cluster]
            cluster_lens = dict(this_cluster['len'].value_counts())
            most_lens = max(cluster_lens.items(), key=operator.itemgetter(1))[0]
            if len(cluster_lens) > 1:
                warnings.warn('Values of different length found to be passed to the Regex Compiler for cluster {}. This is an indication of buggy alignment but can be ignored if values were intentionally not aligned. For now, using values with {} tokens (most dominant length).'.format(cluster, most_lens))

            indices = aligned_series[(aligned_series['cluster'] == cluster) & (aligned_series['len'] == most_lens)].index
            sample[cluster] = aligned_series.loc[indices[0], 'column']
            regex_matrix = aligned_series.loc[indices, pat_column].to_numpy()
            results[cluster], generalized[cluster] = RegexCompiler.generate_regex_from_matrix(regex_matrix)

        if self._aligner is not None:
            anomalous = [-1]
        else:
            anomalous = list()
            for k, v in proportion.items():
                if v < .05:
                    anomalous.append(k)

        self.outliers = aligned_series[aligned_series['cluster'].isin(anomalous)].groupby('column').agg('freq').sum().to_dict()

        result = dict()
        result['Pattern'], result['Generalized'], result['Proportion'], result['Sample'] = results, generalized, proportion, sample
        self.regex = pd.DataFrame(result).reset_index()

        return self.regex
        # return results, generalized, proportion, sample, aligned_series, column_length

    def find(self):
        pat_column = 'tokens'

        series = self.series
        tokenizer = self._tokenizer
        series['tokens'] = tokenizer.tokenize(series['column'])
        series['column_recovered'] = series.tokens.str.join('') # for tokens that were replaced to richer types

        aligned = self._align(series[pat_column]) #todo: fix lingpy to return df:[tokens,cluster] not np array
        self._aligned = aligned['aligned']

        aligned['column_recovered'] = aligned[pat_column].str.join('')
        aligned['aligned_recovered'] = aligned['aligned'].str.join('')

        aligned_series = series.merge(aligned.drop([pat_column], 1), on=['column_recovered'])

        self.clusters = aligned_series[['column','cluster']]

        proportion = dict(aligned_series.groupby('cluster').agg('freq').sum() / aligned_series.freq.sum())
        column_length = aligned_series.freq.sum()
        frequency_dict = aligned_series.groupby('aligned_recovered').agg('freq').sum().to_dict()

        results = dict()
        generalized = dict()
        sample = dict()
        for cluster in aligned_series['cluster'].unique():
            if cluster == -1:
                continue # -1 is the noise cluster with anything that did not align

            this_cluster = aligned_series[aligned_series['cluster'] == cluster]
            cluster_lens = dict(this_cluster['len'].value_counts())
            most_lens = max(cluster_lens.items(), key=operator.itemgetter(1))[0]
            if len(cluster_lens) > 1:
                warnings.warn('Values of different length found to be passed to the Regex Compiler for cluster {}. This is an indication of buggy alignment but can be ignored if values were intentionally not aligned. For now, using values with {} tokens (most dominant length).'.format(cluster, most_lens))

            indices = aligned_series[(aligned_series['cluster'] == cluster) & (aligned_series['len'] == most_lens)].index
            np_aligned_rows = list()
            [np_aligned_rows.append(r) for r in aligned_series.iloc[indices]['aligned']]
            np_aligned_rows = np.array(np_aligned_rows)

            sample[cluster] = np_aligned_rows[0]

            regex_matrix, regex_str = RegexCompiler.compile(aligned_rows=np_aligned_rows, frequency_dict=frequency_dict)
            results[cluster], generalized[cluster] = RegexCompiler.generate_regex_from_matrix(regex_matrix)

        if self._aligner is not None:
            anomalous = [-1]
        else:
            anomalous = list()
            for k, v in proportion.items():
                if v < .05:
                    anomalous.append(k)

        self.outliers = aligned_series[aligned_series['cluster'].isin(anomalous)].groupby('column').agg('freq').sum().to_dict()

        result = dict()
        result['Pattern'], result['Generalized'], result['Proportion'], result['Sample'] = results, generalized, proportion, sample
        self.regex = pd.DataFrame(result).reset_index()

        return self.regex
        # return results, generalized, proportion, sample, aligned_series, column_length

    def evaluate(self, column, encode=False):
        assert isinstance(column, dict) or isinstance(column, list)
        column = self._sample(column, 1)

        def rem_pads(x):
            if len(x) == 1:
                x[0] = x[0][1:-1]
            elif len(x) > 1:
                x[0] = x[0][1:]
                x[-1] = x[-1][:-1]
            return x

        patterns = self.regex[['index','Pattern','Generalized']].dropna(how='any').set_index('index').stack()
        if isinstance(patterns, pd.Series) and not patterns.empty:
            eval_patterns = patterns.str.strip().str.split('\] \[').apply(rem_pads).to_dict()
        else:
            raise TypeError("Incorrect patterns format")

        tokenizer = self._tokenizer
        freq = column.groupby('column').agg('freq').sum().to_dict()
        if encode:
            regex_matrix, _ = tokenizer.encode(column['column'], freq=freq)
            matched = Evaluator.evaluate_matrix(regex_matrix, eval_patterns)
        else:
            column['tokens'] = tokenizer.tokenize(column['column'])
            np_aligned_rows = column['tokens'].tolist()
            matched = Evaluator.evaluate_tokens(np_aligned_rows, freq, eval_patterns)

        return matched
