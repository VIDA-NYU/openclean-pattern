# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""The RegexCompiler class evaluates a RegexPattern from groups of openclean.function.token.base.Token's
"""

from abc import ABCMeta, abstractmethod
from openclean_pattern.regex.base import ColumnPatterns, RowPatterns
import numpy as np


class RegexCompiler(metaclass=ABCMeta):
    """the RegexCompiler class accepts columns grouped by rowidxs on some merit and evaluates
    the best type for each token index per row which can then be serialized into a RegexPattern
     """

    def __init__(self, per_group='top'):
        """Initializes the class

        Parameters
        ----------
        per_group: str
            selects between whether all group patterns should be returned or just the top one
        """
        if per_group not in ['all', 'top']:
            raise ValueError("group aggregation: {} not found".format(per_group))
        self.per_group = per_group

    @abstractmethod
    def compile_each(self, group):
        """
        Accepts individual groups and compiles the pattern
        Parameters
        ----------
        group :  List[List[openclean.function.token.base.Token]]
            tokenized rows

        Returns
        -------
            PatternRows
        """
        raise NotImplementedError()  # pragma: no cover

    def compile(self, tokenized_column, groups):
        """Accepts the tokenized rows and a dict of group indices and returns the patterns per group along
        with their proportions

        Parameters
        ----------
        tokenized_column : List[Tuple[openclean.function.token.base.Tokens]]
            tokenized rows
        groups : Dict[int:List]
            the dict with group label/cluster/size : list of rowidxs

        Returns
        -------
            Dict of format => groups: PatternRows
        """
        # todo: report card
        patterns = dict()
        for gr, rowidxs in groups.items():
            group = [tokenized_column[i] for i in rowidxs]
            patterns[gr] = self.compile_each(group=group)
        return patterns

    def mismatches(self, tokenized_column, patterns):
        """Accepts the tokenized rows and a list of allowed patterns and returns a list of booleans where True is match
        not found (anomaly) whereas False is match found (not anomaly)

        Parameters
        ----------
        tokenized_column : List[Tuple[openclean.function.token.base.Tokens]]
            tokenized rows
        patterns : List
            the list of acceptable patterns

        Returns
        -------
            List of indices
        """

        if not isinstance(patterns, list):
            patterns = [patterns]

        predicates = dict()
        for pattern in patterns:
            if pattern.pattern() not in predicates:
                predicates[pattern.pattern()] = list()
            for row in tokenized_column:
                predicates[pattern.pattern()].append(pattern.compare(row))

        mismatches = np.array([True] * len(tokenized_column))
        for predicate in predicates.values():
            mismatches = mismatches & np.logical_not(predicate)

        return mismatches.tolist()


COMPILER_DEFAULT = 'default'


class DefaultRegexCompiler(RegexCompiler):
    """Compiles the full Regexp using PatternColumns with the top shares"""

    def __init__(self, method='row', per_group='top', size_coverage=1):
        """Initializes the class

        Parameters
        ----------
        method: str
            chooses between row-wise and column-wise aggregations for the compiler
        per_group: str
            selects between whether all group patterns should be returned or just the top one
        size_coverage: float
            sets the threshold for sizes to include e.g. in the 11 rows:

            01 / 01 / 2001 => dig / dig / dig
            31 / 01 / 2002 => dig / dig / dig
            21 / 01 / 2003 => dig / dig / dig
            01 / 02 / 2004 => dig / dig / dig
            23 / 03 / 2015 => dig / dig / dig
            01 / 01 / 2006 => dig / dig / dig
            01 / 01 / 2007 => dig / dig / dig
            6 / 03 / 2012 => dig / dig / dig
            01 / 01 / 2008 => dig / dig / dig
            01 / 01 / 2009 => dig / dig / dig
            11 / 01 / 2010 => dig / dig / dig

            for position 0:
                dig:{
                    2:[] <- 91%
                    1:[] <- 9%
                }

            if size_coverage = 1 , final patternElement => DIGIT[1-2]
            if size_coverage = .9 , final patternElement => DIGIT[2-2]

            the compiler incrementally includes all sized values in the final pattern in descending order
            that add upto the size_coverage. It helps exclude value sizes that appear very rarely

        """
        super(DefaultRegexCompiler, self).__init__(per_group=per_group)

        if method not in ['row', 'col']:
            raise NotImplementedError("{} not found".format(method))
        self.method = method
        self.size_coverage = size_coverage

    def compile_each(self, group):
        """Accepts individual groups and compiles a majority pooled pattern based on the top share

        Parameters
        ----------
        group :  List[List[openclean.function.token.base.Token]]
            tokenized rows

        Returns
        -------
            PatternRows
        """
        patterns = self.pattern_generator()
        for row in group:
            patterns.insert(row)

        # Incase the patterns are calculated differently from the base row
        # calculation method, the condense method converts the format.
        condensed = patterns.condense()

        if self.per_group == 'top':
            top_pattern = condensed.top()
            keys = list(condensed.keys())
            for pattern in keys:
                if pattern != top_pattern:
                    del condensed[pattern]
        return condensed

    def pattern_generator(self):
        """returns the pattern generator method used.
        Todo: move to a factory class
        """
        if self.method == 'row':
            return RowPatterns(self.size_coverage)
        elif self.method == 'col':
            return ColumnPatterns(self.size_coverage)
