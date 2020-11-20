# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

import numpy as np
from collections import defaultdict

from openclean_pattern.tokenize.token import Token
from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.utils.utils import StringComparator


class PatternColumn(defaultdict):
    """
    Token type tracker for each supported datatype that appears in the same column token position
    e.g.
    123 BARCLAY AVE, NY === NUM(3) SPACE ALPHA(7) SPACE STREET PUNC(,) SPACE STATE
    23 NEWTON ST, OH ====== NUM(2) SPACE ALPHA(6) SPACE STREET PUNC(,) SPACE STATE
    ABRA, KADABRA AVE, MN = ALPHA(4) PUNC(,) SPACE ALPHA(7) SPACE STREET PUNC(,) SPACE STATE
    #todo: update this example
    for column token position 0, the RegexTokensPattern would be:
        self.pattern = {
            NUM:
                RegexPatternElement{
                    self.element_type = NUM
                    self.regex = NUM
                    self.len_min = 2
                    self.len_max = 3
                    self.freq = 2
                    self.punc_list = list()
                }
            ALPHA:
                RegexPatternElement{
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

    The insert_token method adds tokens to the respective RegexPatternElement. The final RegexPatternElement is
    condensed by RegexTokensPattern into a Regex Expression for the position
    """

    def __init__(self):
        """initializes the PatternColumn object
        """
        self.global_min = np.inf
        self.global_max = -np.inf
        self.global_freq = 0

    def insert(self, token):
        """inserts/updates the token into the respective PatternColumnElement object

        Parameters
        ----------
        token : Token
            the token to insert/ use to update the respective PatternColumnElement
        """
        if not isinstance(token, Token):
            raise ValueError("expected: openclean_pattern.tokenize.token.Token, got: {}".format(token.__class__))

        if token.regex_type.name in self:
            self[token.regex_type.name].update(token)
        else:
            self[token.regex_type.name] = PatternColumnElement(token)

        self.global_min = min(self.global_min, token.size)
        self.global_max = max(self.global_max, token.size)
        self.global_freq += 1

    def stats(self):
        """calculates shares of each element type in the column

        Returns
        -------
            dict
        """
        shares = defaultdict(float)
        for p in self.values():
            shares[p.element_type] = self[p.element_type].freq / self.global_freq
        return shares

    def get_top(self, n=1):
        """gets the element type with the n ranked share

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

        n -= 1 # change rank to index

        shares = self.stats()
        sorted_shares = sorted(shares.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_shares[n][0]

    def get_anomalies(self):
        """gets the indices of rows that didnt match the majority share element type in this PatternColumn

        Returns
        -------
            list
        """
        top = self.get_top()
        anomalies = list()
        for p in self:
            if p != top:
                [anomalies.append(id) for id in self[p].idx]
        return anomalies


    # todo: deserialize
    def compare_pattern_to_token(self, full_pattern, row_tokens):
        import ast
        inv_supported_type_rep = {v: k for k, v in supported_type_rep.items()}
        match = 0

        custom = list()
        [custom.append(i) for i in supported_type_rep.keys() if i not in [ALPHA, ALPHANUM, DIGIT]]
        for pattern, token in zip(full_pattern, row_tokens):

            # if pattern in custom and token[1] in custom:
            #     print('here')
            # parse pattern
            elements = pattern.split(' | ')
            for e in elements:
                if e.find(OPTIONAL_REP) == 0:
                    element_type = GAP
                    prompt = OPTIONAL_REP
                elif e.find(PUNCTUATION_REP) == 0:
                    element_type = PUNCTUATION
                    prompt = PUNCTUATION_REP
                elif e.find(ALPHANUM_REP) == 0:
                    element_type = ALPHANUM
                    prompt = ALPHANUM_REP
                elif e.find('.*') == 0:
                    element_type = 'WILD'
                    prompt = '.*'
                else:
                    found = False
                    for istr in inv_supported_type_rep.keys():
                        if e.find(istr) == 0 and e.find(ALPHANUM_REP) != 0:
                            element_type = inv_supported_type_rep[istr]
                            prompt = istr
                            found = True
                            break
                    if not found:
                        element_type = 'STATIC'
                        prompt = e.split('(')[0]
                        width = ast.literal_eval("(" + e.split('(')[1].replace('-', ','))

                # if element_type in [ALPHA, ALPHANUM, DIGIT]:
                if element_type in supported_type_rep.keys():
                    width = ast.literal_eval(e.replace(prompt, '').replace('-', ','))
                    if ((token[1] == element_type) \
                        or (token[1] in [ALPHA, DIGIT] and element_type == ALPHANUM)) \
                            and width[0] <= len(token[0]) <= width[1]:
                        match += 1
                        break
                elif element_type == PUNCTUATION:
                    punc_list = list(e.replace(prompt, '').replace(SPACE_REP, ' ')[1:-1])
                    if token[0] in punc_list:
                        match += 1
                        break
                elif element_type == 'STATIC':
                    if self.type_checker.pattern_token_comp(prompt, width, token[0]):
                        match += 1
                        break
                elif element_type == 'WILD':
                    width = ast.literal_eval(e.replace(prompt, '').replace('-', ','))
                    if width[0] <= len(token[0]) <= width[1]:
                        match += 1
                        break

        if match / len(row_tokens) == 1:  # if there's a 100% match b/w the pattern and the row, return frequency
            return True

        return False


class PatternColumnElement(object):
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

        self.punc_list = [] #list of punc tokens if this is a PUNCTUATION elemenet

        self.partial_regex = 23X #partial regex value
        self.partial_ambiguous = False #is partial regex value too ambiguous to be used

        self.freq = 2

    The update_pattern method keeps adding similar type tokens to PatternColumnElement object and once all the tokens have been
    exhausted, the final PatternColumnElement object  is condensed by PatternColumn into a Regex Expression for the position
    """

    def __init__(self, token):
        """initializes the PatternColumnElement and keeps track of numerous stats incrementally as it builds the regexp

        Parameters
        ----------
        token : Token
            the token used to create this PatternColumnElement object
        """
        self.element_type = token.regex_type.name  # type of regex element
        self.regex = token.regex_type.value  # regex representation
        self.len_min = token.size  # min len
        self.len_max = token.size  # max len

        self.idx = list()  # list of indices that went into this element. useful to trace anomalies back to rows
        self.idx.append(token.rowidx)

        self.punc_list = list()  # list of punc tokens if this is a PUNCTUATION elemenet
        if token.regex_type == SupportedDataTypes.PUNCTUATION:
            self.punc_list.append(token.value)

        self.partial_regex = token.value  # partial regex value
        self.partial_ambiguous = False  # is partial regex value too ambiguous to be used

        self.freq = 1  # total frequency of tokens seen (useful for element proportions to identify anomalous patterns)

    def update(self, new_token):
        """updates the PatternColumnElement object

        Parameters
        ----------
        new_token : Token
            the token used to create this PatternColumnElement object

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
        self.idx.append(new_token.rowidx)

    def __str__(self):
        """String representation of the PatternColumnElement object

        Returns
        -------
            str
        """
        if self.element_type == SupportedDataTypes.PUNCTUATION.name:
            return '{}({})'.format(self.regex, ''.join(self.punc_list))

        pattern = self.regex if self.partial_ambiguous else self.partial_regex
        return '{}({}-{})'.format(pattern, self.len_min, self.len_max)
