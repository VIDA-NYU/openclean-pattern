# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""the RegexCompiler class evaluates a RegexPattern from groups of openclean_pattern.tokenize.token.Tokens"""

from abc import ABCMeta, abstractmethod
from openclean_pattern.regex.compiler import PatternColumn, Patterns


class RegexCompiler(metaclass=ABCMeta):
    """the RegexCompiler class accepts columns grouped by rowidxs on some merit and evaluates
    the best type for each token index per row which can then be serialized into a RegexPattern
     """

    @abstractmethod
    def compile_group(self, group):
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
    def group_mismatches(self, group):
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
            patterns[gr] = self.compile_group(group=group)
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
            anomalies[gr] = self.group_mismatches(group=group)
        return anomalies


class DefaultRegexCompiler(RegexCompiler):
    """Compiles the full Regexp using PatternColumns with the top shares"""

    def compile_group(self, group):
        """Accepts individual groups and compiles a majority pooled pattern based on the top share

        Parameters
        ----------
        group :  List[List[openclean_pattern.tokenize.token.Token]]
            tokenized rows

        Returns
        -------
            list of PatternColumnElement
        """
        pattern = list()
        for row in group:
            for i, tok in enumerate(row):
                if len(pattern)-1 < i:
                    pattern.append(PatternColumn())
                pattern[i].insert(tok)

        pooled_pattern = list()
        idxs = set()
        for p in pattern:
            pooled_pattern.append(p.get_top())
            if len(idxs) == 0:
                idxs = set(p[p.get_top()].idx)
            idxs = idxs.intersection(p[p.get_top()].idx)

        return pooled_pattern

    def group_mismatches(self, group):
        """Retrieves the row idxs for rows that didn't match the majority pooled pattern

        Returns
        -------
            set
        """
        pattern = list()
        for row in group:
            for i, tok in enumerate(row):
                if len(pattern)-1 < i:
                    pattern.append(PatternColumn())
                pattern[i].insert(tok)

        anomalies = set()
        for p in pattern:
            anomalies = anomalies.union(set(p.get_anomalies()))

        return anomalies


class RowWiseCompiler(RegexCompiler):
    """Compiles the full Regexp using PatternColumns with the same row pattern"""

    def compile_group(self, group):
        """Accepts individual groups and compiles a majority pooled pattern based on the top share

        Parameters
        ----------
        group :  List[List[openclean_pattern.tokenize.token.Token]]
            tokenized rows

        Returns
        -------
            list of PatternColumnElement
        """
        patterns = Patterns()
        for row in group:
            patterns.insert(row)

        top_pattern = patterns.get_top()
        return patterns[top_pattern]

    def group_mismatches(self, group):
        """Retrieves the row idxs for rows that didn't match the majority pooled pattern

        Returns
        -------
            set
        """
        patterns = Patterns()
        for row in group:
            patterns.insert(row)

        return patterns.get_anomalies()
