# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""the RegexCompiler class evaluates a RegexPattern from groups of openclean_pattern.tokenize.token.Tokens"""

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
        group :  List[List[openclean_pattern.tokenize.token.Tokens]]
            tokenized rows

        Returns
        -------
            PatternRows
        """
        raise NotImplementedError()

    def compile(self, tokenized_column, groups):
        """Accepts the tokenized rows and a dict of group indices and returns the patterns per group along
        with their proportions

        Parameters
        ----------
        tokenized_column : List[Tuple[openclean_pattern.tokenize.token.Tokens]]
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
        tokenized_column : List[Tuple[openclean_pattern.tokenize.token.Tokens]]
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

    def __init__(self, method='row', per_group='top'):
        """Initializes the class

        Parameters
        ----------
        method: str
            chooses between row-wise and column-wise aggregations for the compiler
        per_group: str
            selects between whether all group patterns should be returned or just the top one
        """
        super(DefaultRegexCompiler, self).__init__(per_group=per_group)

        if method not in ['row', 'col']:
            raise NotImplementedError("{} not found".format(method))
        self.method = method

    def compile_each(self, group):
        """Accepts individual groups and compiles a majority pooled pattern based on the top share

        Parameters
        ----------
        group :  List[List[openclean_pattern.tokenize.token.Token]]
            tokenized rows

        Returns
        -------
            PatternRows
        """
        patterns = self.pattern_generator()
        for row in group:
            patterns.insert(row)

        # incase the patterns are calculated differently from the base row calculation method, the condense method
        # converts the format
        condensed = patterns.condense()

        if self.per_group == 'top':
            top_pattern = condensed.top()
            keys = list(condensed.keys())
            for pattern in keys:
                if pattern != top_pattern:
                    del condensed[pattern]
        return condensed

    def pattern_generator(self):
        """returns the pattern generator mathod used.
        Todo: move to a factory class
        """
        if self.method == 'row':
            return RowPatterns()
        elif self.method == 'col':
            return ColumnPatterns()
