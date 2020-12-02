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
from openclean_pattern.evaluate.evaluator import Evaluator

from openclean_pattern.utils.utils import WeightedRandomSampler, Distinct
from openclean_pattern.regex.base import Pattern

import pandas as pd

from typing import Union, List, Dict
from collections import Counter


class PatternFinder(object):
    """
    PatternFinder class to identify patterns and anomalies
    """

    def __init__(self,
                 frac: float = 1,
                 distinct: bool = True,
                 tokenizer: Union[str, Tokenizer] = TOKENIZER_DEFAULT,
                 aligner: Union[str, Aligner] = ALIGN_GROUP,
                 compiler: RegexCompiler = None) -> None:
        """
        Initialize the pattern finder class. This assumes that the input columns have been sampled if too large

        Parameters
        ----------
        frac: float
            sample size
        tokenizer: str or object of class Tokenizer (default: 'default')
            the tokenizer to use
        aligner: str (default: 'group')
            the aligner to use
        """
        self.frac = frac
        self.distinct = distinct
        self._tokenizer = tokenizer if isinstance(tokenizer, Tokenizer) else TokenizerFactory.create_tokenizer(
            tokenizer)
        self._aligner = aligner if isinstance(aligner, Aligner) else AlignerFactory.create_aligner(aligner)
        self._aligned = None
        self.regex = None
        self.outliers = dict()
        self._compiler = compiler if compiler is not None else DefaultRegexCompiler()

    def _sample(self, series: Union[List, Dict, pd.Series], frac: float, distinct: bool):
        '''
        randomly samples large columns and resolves frequency

        Parameters
        ----------
        series: list or dict or pd.Series
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

    def compare(self, pattern: Pattern, values: Union[List[str], str], negate=False):
        """Get an instance of a value function that is predicate which can be
        used to test whether an given value is accepted by the pattern or not.

        Parameters
        ----------
        pattern : Pattern
            The pattern to evaluate the values against
        values :  List[str] or str
            The value or list of values
        negate: bool, default=False
            If the negate flag is True, the returned predicate should return
            True for values that are not accepted by the pattern and False for
            those that are accepted.

        Returns
        -------
        list[bool]
        """

        if isinstance(values, str):
            values = [values]

        tokenizer = self._tokenizer
        tokenized = tokenizer.encode(values)

        predicate = list()
        for row in tokenized:
            compared = Evaluator.compare(pattern, row)
            compared = compared if not negate else not compared
            predicate.append(compared)

        return predicate

    def find(self, series: Union[Dict, List, pd.Series]):
        """ identifies patterns present in the provided columns and returns a list of tuples in the form (pattern, proportions)

        Parameters
        ----------
         series: list or dict or pd.Series
            list of column values or dict of column values:frequency

        Returns
        -------
            RowPattern(s)
        """
        column = self._sample(series=series, frac=self.frac, distinct=self.distinct)
        tokenizer = self._tokenizer
        aligner = self._aligner
        compiler = self._compiler

        # encode is a two step method. it does both, the tokenization and the type resolution in the same go
        tokenized = tokenizer.encode(column)
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
