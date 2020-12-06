# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""the RegexCompiler class evaluates a RegexPattern from groups of openclean_pattern.tokenize.token.Tokens"""

from abc import ABCMeta, abstractmethod
from openclean_pattern.regex.base import ColumnPatterns, RowPatterns


class RegexCompiler(metaclass=ABCMeta):
    """the RegexCompiler class accepts columns grouped by rowidxs on some merit and evaluates
    the best type for each token index per row which can then be serialized into a RegexPattern
     """

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
            list of PatternColumnElement
        """
        raise NotImplementedError()

    @abstractmethod
    def anomalies_each(self, group):
        """Retrieves the row idxs for rows that didn't match the majority pooled pattern

        Returns
        -------
            set
        """
        raise NotImplementedError()

    def compile(self, tokenized_column, groups):
        """Accepts the tokenized rows and a dict of group indices and returns the patterns per group along
        with their proportions

        Parameters
        ----------
        tokenized_column : List[List[openclean_pattern.tokenize.token.Tokens]]
            tokenized rows
        groups : Dict[int:List]
            the dict with group label/cluster/size : list of rowidxs

        Returns
        -------
            Dict of groups: PatternTokens
        """
        # todo: report card
        patterns = dict()
        for gr, rowidxs in groups.items():
            group = [tokenized_column[i] for i in rowidxs]
            patterns[gr] = self.compile_each(group=group)
        return patterns

    def anomalies(self, tokenized_column, groups):
        """Accepts the tokenized rows and a dict of group indices and returns the index of the anomalies per group

        Parameters
        ----------
        tokenized_column : List[List[openclean_pattern.tokenize.token.Tokens]]
            tokenized rows
        groups : Dict[int:List]
            the dict with group label/cluster/size : list of rowidxs

        Returns
        -------
        Dict of groups: set
        """
        anomalies = dict()
        for gr, rowidxs in groups.items():
            group = [tokenized_column[i] for i in rowidxs]
            anomalies[gr] = self.anomalies_each(group=group)
        return anomalies


COMPILER_DEFAULT = 'default'

class DefaultRegexCompiler(RegexCompiler):
    """Compiles the full Regexp using PatternColumns with the top shares"""
    def __init__(self, method='row'):
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
            list of PatternColumnElement
        """
        patterns = self.pattern_generator()
        for row in group:
            patterns.insert(row)

        # incase the patterns are calculated differently from the base row calculation method, the condense method
        # converts the format
        condensed = patterns.condense()

        top_pattern = condensed.top()
        return condensed[top_pattern]

    def anomalies_each(self, group):
        """Retrieves the row idxs for rows that didn't match the majority pooled pattern

        Returns
        -------
            set
        """
        patterns = self.pattern_generator()
        for row in group:
            patterns.insert(row)

        # incase the patterns are calculated differently from the base row calculation method, the condense method
        # converts the format
        condensed = patterns.condense()

        return condensed.anomalies()

    def pattern_generator(self):
        """returns the pattern generator mathod used.
        Todo: move to a factory class
        """
        if self.method == 'row':
            return RowPatterns()
        elif self.method == 'col':
            return ColumnPatterns()
