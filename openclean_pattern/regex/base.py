# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""classes of base Pattern objects"""

import numpy as np
from collections import defaultdict
from abc import abstractmethod, ABCMeta

from openclean_pattern.tokenize.token import Token
from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.utils.utils import StringComparator


### Row/Column Pattern

class Pattern(metaclass=ABCMeta):
    """Contains PatternElements used inside the Patterns class to store a single row / column pattern"""

    def __init__(self, container):
        """Initialize the Pattern class"""
        self.container = container
        self.freq = 0
        self.idx = set()

    @abstractmethod
    def update(self, tokens):
        """update using the tokens, the list (of Pattern Elements

        Parameters
        ----------
         tokens: Token
            the tokens to use create the Pattern
        """
        raise NotImplementedError()

    def evaluate(self, value):
        """Evaluates the given value against the pattern and returns a boolean

        Parameters
        ----------
        value: str
            value to compare with the pattern
        """
        raise NotImplementedError()

    def __iter__(self):
        return iter(self.container)

    def __repr__(self):
        return str(self.container)

    def __len__(self):
        return len(self.container)


class SingularRowPattern(Pattern):
    """Class to create / store a singular pattern created from a row / condensed into a row form"""

    def __init__(self):
        """initializes the class"""
        container = list()
        super(SingularRowPattern, self).__init__(container)

    def update(self, tokens):
        """update using the tokens, the list (of Pattern Elements

        Parameters
        ----------
         tokens: Token
            the tokens to use create the Pattern
        """
        for r, e in zip(tokens, self.container):
            if e.element_type != r.regex_type.name:
                raise TypeError("incompatible row inserted")
            e.update(r)

        self.idx.add(r.rowidx)
        self.freq += 1

    def __eq__(self, other):
        for s, o in zip(self, other):
            if s.element_type != o.element_type:
                return False
        return len(self) == len(other)


class SingularColumnPattern(Pattern):
    """Class to create / store a singular patterns created from a row"""

    def __init__(self):
        """initializes the class"""
        container = dict()
        super(SingularColumnPattern, self).__init__(container)
        self.column_min = np.inf
        self.column_max = -np.inf
        self.column_freq = 0

    def update(self, tokens):
        """update the column pattern using the tokens, the list (of Pattern Elements

        Parameters
        ----------
         tokens: Token
            the tokens to use create the Pattern
        """
        if isinstance(tokens, Token):
            tokens = [tokens]
        for token in tokens:
            if not isinstance(token, Token):
                raise TypeError("expected: openclean_pattern.tokenize.token.Token, got: {}".format(token.__class__))

            if token.regex_type.name not in self.container:
                self.container[token.regex_type.name] = PatternElement(token)
            else:
                self.container[token.regex_type.name].update(token)

        self.idx.add(token.rowidx)
        self.column_freq += 1
        self.column_min = min(self.column_min, token.size)
        self.column_max = max(self.column_max, token.size)

    def top(self):
        """returns the top PatternElement in the column

        Returns
        -------
            PatternElement
        """
        max = -np.inf
        top = None
        for i, c in self.container.items():
            if c.freq > max:
                top = c
                max = top.freq
        return top


### Pattern Dicts


class Patterns(defaultdict, metaclass=ABCMeta):
    """Class to create patterns from tokens"""

    def __init__(self):
        super(Patterns, self).__init__()
        self.global_freq = 0
        self.anoms = set()

    @staticmethod
    def keygen(row):
        """converts the row types into the key for the Patterns class"""
        key = ''
        for r in row:
            key += '|' + str(r)
        return key.strip()

    @abstractmethod
    def insert(self, row):
        """insert the row into the respective method"""
        raise NotImplementedError()

    @abstractmethod
    def condense(self):
        """converts the patterns class to the default representation incase they were compiled using a different method

        Returns
        -------
            RowPatterns
        """
        raise NotImplementedError()

    def stats(self):
        """calculates shares of each Pattern. Ensure this is computed on the Patterns.condensed() object

        Returns
        -------
            dict
        """
        shares = defaultdict(float)
        for p in self:
            shares[p] = self[p].freq / self.global_freq
        return shares

    def top(self, n=1):
        """gets the element type with the n ranked share. Ensure this is computed on the Patterns.condensed() object

        Parameters
        ----------
        n: int
            ranking

        Returns
        -------
            str / int
        """
        if n < 1:
            raise ValueError("rank should be greater than zero")

        n -= 1  # change rank to index

        shares = self.stats()
        sorted_shares = sorted(shares.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_shares[n][0]

    def anomalies(self, n=1):
        """gets the indices of rows that didnt match the nth pattern. Ensure this is computed on the
         Patterns.condensed() object

        Parameters
        ----------
        n: int
            rank of pattern to pick

        Returns
        -------
            list
        """
        top = self.top(n=n)
        anomalies = list()
        for p in self:
            if p != top:
                [anomalies.append(id) for id in self[p].idx]
            elif p == top:
                pattern = self[p]
                all_idxs = set()
                for pat in pattern.container:
                    all_idxs.update(pat.idx)

                [anomalies.append(ix) for ix in all_idxs if ix not in pattern.idx]

        return anomalies

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        eq = len(self) == len(other)
        for s, o in zip(self, other):
            eq = eq and s == o
        return eq and self.global_freq == other.global_freq

    def __repr__(self):
        vals = ''
        for i in self:
            vals += str(i)
        return '{}({})'.format(self.__class__.__name__, vals)


class RowPatterns(Patterns):
    """Token type tracker for each distinct pattern that appears in the rows
    """

    def __init__(self):
        """initializes the row object

        Parameters
        ----------
        row :  list of Tokens
            the list to evaluate the patterns from
        """
        super(RowPatterns, self).__init__()

    def insert(self, row):
        """Inserts a row into the discovered patterns or updates the PatternRow object

        Parameters
        ----------
        row : list of Tokens
        """

        self.global_freq += 1
        types = list()
        [types.append(i.regex_type.name) for i in row]

        key = Patterns.keygen(types)

        if key not in self:
            self[key] = SingularRowPattern()
            for r in row:
                self[key].container.append(PatternElement(r))
            self[key].freq += 1
            self[key].idx.add(r.rowidx)
        else:
            self[key].update(row)

    def condense(self):
        """converts the patterns class to the default representation incase they were compiled using a different method

        Returns
        -------
            RowPatterns
        """
        return self


class ColumnPatterns(Patterns):
    """
    Token type tracker for each supported datatype that appears in the same column token position
    e.g.
    123 BARCLAY AVE, NY === NUM(3) SPACE ALPHA(7) SPACE STREET PUNC(,) SPACE STATE
    23 NEWTON ST, OH ====== NUM(2) SPACE ALPHA(6) SPACE STREET PUNC(,) SPACE STATE
    ABRA, KADABRA AVE, MN = ALPHA(4) PUNC(,) SPACE ALPHA(7) SPACE STREET PUNC(,) SPACE STATE
    for column token position 0, the Pattern components would be:
        {
            NUM:
                PatternElement{
                    self.element_type = NUM
                    self.regex = NUM
                    self.len_min = 2
                    self.len_max = 3
                    self.freq = 2
                    self.punc_list = list()
                }
            ALPHA:
                PatternElement{
                    self.element_type = ALPHA
                    self.regex = ALPHA
                    self.len_min = 4
                    self.len_max = 4
                    self.freq = 1
                    self.punc_list = list()
                }
        }
        self.global_min = 2
        self.global_max = 4
        self.global_freq = 3

    The insert method adds tokens to the respective PatternElement. The final PatternElements are
    condensed into a Regex Expression as a RowPatterns
    """

    def __init__(self):
        """initializes the PatternColumn object
        """
        super(ColumnPatterns, self).__init__()

    def insert(self, row):
        """insert the row into the respective method

        Parameters
        ----------
        token : Token
            the token to insert/ use to update the respective PatternColumnElement
        """
        self.global_freq += 1
        for key, token in enumerate(row):
            if not isinstance(token, Token):
                raise TypeError("expected: openclean_pattern.tokenize.token.Token, got: {}".format(token.__class__))

            if key not in self:
                self[key] = SingularColumnPattern()

            self[key].update(token)

    def condense(self):
        """finds the top element in each column and returns the derived pattern

        Returns
        -------
            RowPatterns
        """
        pattern = list()
        for ind, col in self.items():
            pattern.append(col.top())

        types = list()
        [types.append(i.element_type) for i in pattern]

        key = Patterns.keygen(pattern)

        patterns = RowPatterns()
        patterns[key] = SingularRowPattern()

        # add patterns and idx and freq of pattern
        for pat in pattern:
            patterns[key].container.append(pat)

            # calculate intersection of all indices as the indices of interest
            if len(patterns[key].idx) == 0:
                patterns[key].idx = pat.idx
            else:
                patterns[key].idx = patterns[key].idx.intersection(pat.idx)

            patterns[key].freq = len(patterns[key].idx)

        # add global freq (total rows)
        patterns.global_freq = self.global_freq

        return patterns


### Pattern element / building blocks


class PatternElement(object):
    """
    Element tracker for a single supported datatype that appear in the same column token position
    e.g.
    231 BARCLAY AVE, NY === NUM(3) SPACE ALPHA(7) SPACE STREET PUNC(,) SPACE STATE
    23 NEWTON ST, OH ====== NUM(2) SPACE ALPHA(6) SPACE STREET PUNC(,) SPACE STATE

    for column token position 0, the PatternColumnElement object  would be:

        self.element_type = DIGIT #type of regex element
        self.regex = NUMERIC #regex representation
        self.len_min = 2 #min len
        self.len_max = 3 #max len

        self.idx = [0, 1] #list of indices that went into this element. useful to trace anomalies back to rows

        self.punc_list = [] #list of punc tokens if this is a PUNCTUATION element

        self.partial_regex = 23X #partial regex value
        self.partial_ambiguous = False #is partial regex value too ambiguous to be used

        self.freq = 2

    The update_pattern method keeps adding similar type tokens to PatternColumnElement object and once all the tokens have been
    exhausted, the final PatternColumnElement object  is condensed by PatternColumn into a Regex Expression for the position
    """

    def __init__(self, token):
        """initializes the PatternElement and keeps track of numerous stats incrementally as it builds the regexp

        Parameters
        ----------
        token : Token
            the token used to create this PatternElement object
        """
        self.element_type = token.regex_type.name  # type of regex element
        self.regex = token.regex_type.value  # regex representation
        self.len_min = token.size  # min len
        self.len_max = token.size  # max len

        self.idx = set()  # list of indices that went into this element. useful to trace anomalies back to rows
        self.idx.add(token.rowidx)

        self.punc_list = list()  # list of punc tokens if this is a PUNCTUATION elemenet
        if token.regex_type == SupportedDataTypes.PUNCTUATION:
            self.punc_list.append(token.value)

        self.partial_regex = token.value  # partial regex value
        self.partial_ambiguous = False  # is partial regex value too ambiguous to be used

        self.freq = 1  # total frequency of tokens seen (useful for element proportions to identify anomalous patterns)

    def update(self, new_token):
        """updates the PatternElement object

        Parameters
        ----------
        new_token : Token
            the token used to create this PatternElement object

        """
        if new_token.regex_type == SupportedDataTypes.PUNCTUATION and new_token.value not in self.punc_list:
            self.punc_list.append(new_token.value)
        elif not self.partial_ambiguous:
            unknown_threshold = 0.8
            # todo: because partial regex is built incrementally too, the order of token.values can have a huge impact on the results. Is there another way?
            new_partial_regex, ambiguity_ratio = StringComparator.compare_strings(self.partial_regex, new_token.value)
            if ambiguity_ratio > unknown_threshold:
                self.partial_ambiguous = True
            self.partial_regex = new_partial_regex
        self.len_min = min(self.len_min, new_token.size)
        self.len_max = max(self.len_max, new_token.size)
        self.freq += 1
        self.idx.add(new_token.rowidx)

    def __str__(self):
        """String representation of the PatternElement object

        Returns
        -------
            str
        """
        if self.element_type == SupportedDataTypes.PUNCTUATION.name:
            return '{}({})'.format(self.regex, ''.join(self.punc_list))

        pattern = self.regex if self.partial_ambiguous else self.partial_regex
        return '{}({}-{})'.format(pattern, self.len_min, self.len_max)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.element_type)

    def __eq__(self, other):
        return self.element_type == other.element_type and \
               self.regex == other.regex and \
               self.len_min == other.len_min and \
               self.len_max == other.len_max and \
               self.idx == other.idx and \
               self.punc_list == other.punc_list and \
               self.partial_regex == other.partial_regex and \
               self.partial_ambiguous == other.partial_ambiguous and \
               self.freq == other.freq
