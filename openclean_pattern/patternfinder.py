# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Pattern Finder class to identify regex patterns, find anomalies and evaluate patterns on new columns"""

from openclean_pattern.tokenize.factory import TokenizerFactory
from openclean_pattern.tokenize.regex import TOKENIZER_DEFAULT
from openclean_pattern.tokenize.base import Tokenizer

from openclean_pattern.align.factory import AlignerFactory
from openclean_pattern.align.group import ALIGN_GROUP
from openclean_pattern.align.base import Aligner

from openclean_pattern.regex.compiler import DefaultRegexCompiler, RegexCompiler
# from openclean_pattern.evaluate import Evaluator

from openclean_pattern.utils.utils import WeightedRandomSampler, Distinct

import numpy as np, pandas as pd, operator, warnings

from typing import Union, List, Dict
from collections import Counter


class PatternFinder(object):
    """
    PatternFinder class to identify patterns and anomalies
    """

    def __init__(self,
                 series: Union[Dict, List],
                 frac: float = 1,
                 distinct: bool = True,
                 tokenizer: Union[str, Tokenizer] = TOKENIZER_DEFAULT,
                 aligner: Union[str, Aligner] = ALIGN_GROUP,
                 compiler: RegexCompiler = None) -> None:
        """
        Initialize the pattern finder class. This assumes that the input columns have been sampled if too large

        Parameters
        ----------
        series: list or dict
            list of column values or dict of column values:frequency
        frac: float
            sample size
        tokenizer: str or object of class Tokenizer (default: 'default')
            the tokenizer to use
        aligner: str (default: 'group')
            the aligner to use
        """
        self.series = self._sample(series, frac, distinct)
        self._tokenizer = tokenizer if isinstance(tokenizer, Tokenizer) else TokenizerFactory.create_tokenizer(
            tokenizer)
        self._aligner = aligner if isinstance(aligner, Aligner) else AlignerFactory.create_aligner(aligner)
        self._aligned = None
        self.regex = None
        self.outliers = dict()
        self._compiler = compiler if compiler is not None else DefaultRegexCompiler()

    def _sample(self, series, frac, distinct):
        '''
        randomly samples large columns and resolves frequency

        Parameters
        ----------
        series: list or dict
            list of column values or dict of column values:frequency
        param frac:  int
            distance to use for clustering
        distinct: bool (default: True)
            if only distinct values should be used to generate patterns and anomalies

        Returns
        -------
            list of samples selected from the input sequence
        '''
        if distinct:
            if isinstance(series, pd.Series):
                series = series.to_list()
            if isinstance(series, list):
                return Distinct(str.replace(str.lower(str(s)), '\'', '') for s in series).sample()
            elif isinstance(series, dict):
                lst = [str.replace(str.lower(str(s)), '\'', '') for s in series.values()]
                return Distinct(lst).sample()

        # to prevent ordering change incase frac == 1
        if frac == 1:
            if isinstance(series, pd.Series):
                series = series.to_list()
            if isinstance(series, list):
                return [str.replace(str.lower(str(s)), '\'', '') for s in series]
            elif isinstance(series, dict):
                return WeightedRandomSampler.counter_to_list(Counter({str.replace(str.lower(str(s)), '\'', ''): i for s, i in series.items()}))

        # for now, remove apostrophes
        if isinstance(series, pd.Series):
            series = series.to_list()
        if isinstance(series, dict):
            series = Counter({str.replace(str.lower(str(s)), '\'', ''): i for s, i in series.items()})
        elif isinstance(series, list):
            series = Counter([str.replace(str.lower(str(s)), '\'', '') for s in series])
        else:
            raise ValueError("Input column not valid")

        return WeightedRandomSampler(weights=series, n=frac, random_state=42).sample()

    def _align(self, tokens):
        '''
        align - memoized. Default alignment is the light weight version which only aggregates by # of tokens
        :param tokens: list of tokenized column values
        :type tokens: pd.Series
        :return: numpy array / df
        '''
        if self._aligned is None:
            if self._aligner is not None:
                aligned = self._aligner.get_aligned(
                    tokens.tolist())
            else:
                aligned = pd.DataFrame(tokens)
                aligned['cluster'] = tokens.apply(len)
                aligned['aligned'] = tokens

            aligned['pre_align_tokens'] = tokens
            aligned['len'] = aligned['aligned'].str.len()

            self._aligned = aligned
        return self._aligned

    # def evaluate(self, column, encode=False):
    #     assert isinstance(column, dict) or isinstance(column, list)
    #     column = self._sample(column, 1)
    #
    #     def rem_pads(x):
    #         if len(x) == 1:
    #             x[0] = x[0][1:-1]
    #         elif len(x) > 1:
    #             x[0] = x[0][1:]
    #             x[-1] = x[-1][:-1]
    #         return x
    #
    #     patterns = self.regex[['index', 'Pattern', 'Generalized']].dropna(how='any').set_index('index').stack()
    #     if isinstance(patterns, pd.Series) and not patterns.empty:
    #         eval_patterns = patterns.str.strip().str.split('\] \[').apply(rem_pads).to_dict()
    #     else:
    #         raise TypeError("Incorrect patterns format")
    #
    #     tokenizer = self._tokenizer
    #     freq = column.groupby('column').agg('freq').sum().to_dict()
    #     if encode:
    #         regex_matrix, _ = tokenizer.encode(column['column'], freq=freq)
    #         matched = Evaluator.evaluate_matrix(regex_matrix, eval_patterns)
    #     else:
    #         column['tokens'] = tokenizer.tokenize(column['column'])
    #         np_aligned_rows = column['tokens'].tolist()
    #         matched = Evaluator.evaluate_tokens(np_aligned_rows, freq, eval_patterns)
    #
    #     return matched

    def find(self):
        """ identifies patterns present in the provided columns and returns a list of tuples in the form (pattern, proportions)
        """
        column = self.series
        tokenizer = self._tokenizer
        aligner = self._aligner
        compiler = self._compiler

        tokenized = tokenizer.encode(
            column)  # encode is a two step method. it does both, the tokenization and the type resolution in the same go
        self._aligned = aligner.align(tokenized)

        self.regex = compiler.compile(tokenized, self._aligned)
        self.outliers = compiler.anomalies(tokenized, self._aligned)

        return self.regex

    def top(self, n=1):
        """ get the nth top pattern

        Parameters
        ----------
        n: int
            the rank
        """
        if self.regex is None:
            self.find()

        if n < 1:
            raise ValueError("rank should be greater than zero")

        n -= 1  # change rank to index

        shares = dict()
        for key, pattern in self.regex.items():
            shares[pattern] = pattern.freq / len(self.series)

        sorted_shares = sorted(shares.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_shares[n][0]
