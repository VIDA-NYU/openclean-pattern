# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""OpencleanPattern Finder class to identify regex patterns, find mismatches and evaluate patterns on new columns"""

from openclean.function.token.base import Tokenizer

from openclean_pattern.tokenize.factory import TokenizerFactory
from openclean_pattern.tokenize.regex import TOKENIZER_DEFAULT

from openclean_pattern.align.factory import AlignerFactory
from openclean_pattern.collect.factory import CollectorFactory
from openclean_pattern.collect.group import COLLECT_GROUP
from openclean_pattern.align.pad import ALIGN_PAD
from openclean_pattern.align.base import Aligner
from openclean_pattern.collect.base import Collector

from openclean_pattern.regex.compiler import RegexCompiler, COMPILER_DEFAULT
from openclean_pattern.regex.factory import CompilerFactory
from openclean_pattern.evaluate.evaluator import Evaluator

from openclean_pattern.utils.utils import WeightedRandomSampler, Distinct
from openclean_pattern.regex.base import OpencleanPattern

import pandas as pd

from typing import Union, List, Dict
from collections import Counter

from openclean.profiling.pattern.base import PatternFinder
from openclean.profiling.base import ProfilerResult


class OpencleanPatternFinder(PatternFinder):
    """
    OpencleanPatternFinder class to identify patterns and mismatches
    """

    def __init__(self,
                 frac: float = 1,
                 distinct: bool = True,
                 tokenizer: Union[str, Tokenizer] = TOKENIZER_DEFAULT,
                 collector: Union[str, Collector] = COLLECT_GROUP,
                 aligner: Union[str, Aligner] = ALIGN_PAD,
                 compiler: Union[str, RegexCompiler] = COMPILER_DEFAULT) -> None:
        """
        Initialize the pattern finder class. This assumes that the input columns have been sampled if too large

        Parameters
        ----------
        frac: float (default = 1)
            sample size
        distinct: bool (default = True)
            set to true to only use distinct patterns to computer patterns
        tokenizer: str or object of class Tokenizer (default: 'default')
            the tokenizer to use
        collector: str or Collector (default: 'group')
            aggregates tokens into similar groups
        aligner: str (default: 'pad')
            the aligner to use
        compiler: RegexCompiler (default: 'default')
            compiles the aligned tokens into Pattern objects
        """
        super(OpencleanPatternFinder, self).__init__()
        self.frac = frac
        self.distinct = distinct
        self._tokenizer = tokenizer if isinstance(tokenizer, Tokenizer) else TokenizerFactory.create_tokenizer(
            tokenizer)
        self._collector = collector if isinstance(collector, Collector) else CollectorFactory.create_collector(
            collector)
        self._aligner = aligner if isinstance(aligner, Aligner) else AlignerFactory.create_aligner(aligner)
        self._aligned = None
        self.patterns = None
        self.outliers = dict()
        self._compiler = compiler if isinstance(compiler, RegexCompiler) else CompilerFactory.create_compiler(compiler)

    def process(self, values: Counter) -> ProfilerResult:
        """Compute one or more features over a set of distinct values. This is
        the main profiling function that computes statistics or informative
        summaries over the given data values. It operates on a compact form of
        a value list that only contains the distinct values and their frequency
        counts.

        The return type of this function is a dictionary. The elements and
        structure in the dictionary are implementation dependent.

        Parameters
        ----------
        values: collections.Counter
            Set of distinct scalar values or tuples of scalar values that are
            mapped to their respective frequency count.

        Returns
        -------
        dict or list
        """
        return self.find(list(values.keys()))

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
            if only distinct values should be used to generate patterns and mismatches

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

    @property
    def tokenizer(self):
        """Get the associated tokenizer.

        Returns
        -------
        openclean.function.token.base.Tokenizer
        """
        return self._tokenizer

    def compare(self, pattern: OpencleanPattern, values: Union[List[str], str], negate=False):
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
        tokenized = self._parse(values)
        predicate = list()
        for row in tokenized:
            compared = Evaluator.compare(pattern, row, self)
            compared = compared if not negate else not compared
            predicate.append(compared)

        return predicate[0] if len(values) == 1 else predicate

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
        self.values = column
        tokenizer = self._tokenizer
        collector = self._collector
        aligner = self._aligner
        compiler = self._compiler

        # encode is a two step method. it does both, the tokenization and the type resolution in the same go
        tokenized = tokenizer.encode(column)
        groups = collector.collect(tokenized)
        self._aligned = aligner.align(tokenized, groups)

        self.patterns = compiler.compile(self._aligned, groups)

        # by default, the top pattern in each group is considered non anomalous
        mismatches = list()
        for pattern in self.patterns.values():
            mismatches.append(pattern.top(pattern=True))

        self.outliers = compiler.mismatches(self._aligned, mismatches)

        return self.patterns

    def _parse(self, value):
        """parses values to the internal 'Tokens' representation
        """
        tokenizer = self._tokenizer
        return tokenizer.encode(value)
