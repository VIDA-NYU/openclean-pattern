from openclean.utils.utils import TypeChecker
from openclean.regex import *

import numpy as np


class RegexPattern:
    '''
    #todo: Serialize all Final piecewise patterns here and condense to produce string outputs.
    This should also deserialize string patterns for evaluator class
    '''

    def __init__(self):
        pass

    @staticmethod
    def from_string(pattern):
        # todo: complete this
        def rem_pads(x):
            if len(x) == 1:
                x[0] = x[0][1:-1]
            elif len(x) > 1:
                x[0] = x[0][1:]
                x[-1] = x[-1][:-1]
            return x

        if isinstance(pattern, str):
            eval_pattern = rem_pads(pattern.strip().split('\] \['))
        else:
            raise TypeError("Incorrect patterns format")

        raise NotImplementedError()


class RegexTokensPattern:
    '''
    Token type tracker for each supported datatype that appears in the same column token position
    e.g.
    123 BARCLAY AVE, NY === NUM(3) SPACE ALPHA(7) SPACE STREET PUNC(,) SPACE STATE
    23 NEWTON ST, OH ====== NUM(2) SPACE ALPHA(6) SPACE STREET PUNC(,) SPACE STATE
    ABRA, KADABRA AVE, MN = ALPHA(4) PUNC(,) SPACE ALPHA(7) SPACE STREET PUNC(,) SPACE STATE

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
    '''

    def __init__(self):
        self.pattern = dict()
        self.global_min = np.inf
        self.global_max = -np.inf
        self.global_freq = 0
        self.type_checker = TypeChecker()

    def get_type_checker(self):
        return self.type_checker

    def insert_token(self, token):
        if len(token) != 3:
            raise ValueError("token tuple of length 3 expected: (token_value, token_type, token_frequency)")
        if token[1] in self.pattern:
            self.pattern[token[1]].update_pattern(token, self.type_checker)
        else:
            self.pattern[token[1]] = RegexPatternElement(token)
        self.global_min = min(self.global_min, len(token[0]))
        self.global_max = max(self.global_max, len(token[0]))
        self.global_freq += int(token[2])

    def condense(self):
        from collections import defaultdict
        strict_pattern = self.pattern.values()
        strict_regex = '[' + ' | '.join(list(map(lambda x: x.get_pattern(), strict_pattern))) + ']'

        generalized_regex = strict_regex
        non_anomalous_types = list()
        shares = defaultdict(float)
        for p in self.pattern:
            shares[p] = self.pattern[p].get_freq() / self.global_freq
            # only use types that show nonanomalous proportions - 5%
            if shares[p] > .05:
                non_anomalous_types.append(p)

        if len(non_anomalous_types) > 1:
            if PUNCTUATION in non_anomalous_types:
                generalized_regex = '[.*({}-{})]'.format(self.global_min, self.global_max)
            elif ALPHANUM in non_anomalous_types or (ALPHA in non_anomalous_types and DIGIT in non_anomalous_types):
                generalized_regex = '[{}({}-{})]'.format(ALPHANUM_REP, self.global_min, self.global_max)
            else:
                sorted_dict = sorted(shares, key=shares.get, reverse=True)
                generalized_regex = '[{}({}-{})]'.format(supported_type_rep[sorted_dict[0]], self.global_min,
                                                         self.global_max)
            if GAP in non_anomalous_types:
                generalized_regex += '[{}]'.format(OPTIONAL_REP)
        elif len(non_anomalous_types) == 1:
            if non_anomalous_types[0] in [PUNCTUATION, GAP]:
                generalized_regex = '[{}]'.format(self.pattern[non_anomalous_types[0]].get_pattern())
            else:
                if non_anomalous_types[0] == ALPHA:
                    t = ALPHA_REP
                elif non_anomalous_types[0] == ALPHANUM:
                    t = ALPHANUM_REP
                elif non_anomalous_types[0] == DIGIT:
                    t = DIGIT_REP
                else:
                    t = supported_type_rep[non_anomalous_types[0]]
                generalized_regex = '[{}({}-{})]'.format(t, self.global_min, self.global_max)

        return strict_regex, generalized_regex

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


class RegexPatternElement(RegexTokensPattern):
    '''
    Element tracker for a single supported datatype that appear in the same column token position
    e.g.
    123 BARCLAY AVE, NY === NUM(3) SPACE ALPHA(7) SPACE STREET PUNC(,) SPACE STATE
    23 NEWTON ST, OH ====== NUM(2) SPACE ALPHA(6) SPACE STREET PUNC(,) SPACE STATE

    for column token position 0, the RegexPatternElement would be:
        self.element_type = NUM
        self.regex = NUM
        self.len_min = 2
        self.len_max = 3
        self.freq = 2
        self.punc_list = list()

    The update_pattern method keeps adding similar type tokens to RegexPatternElement and once all the tokens have been
    exhausted, the final RegexPatternElement is condensed by RegexTokensPattern into a Regex Expression for the position
    '''

    def __init__(self, token):
        self.element_type = token[1]
        self.regex = PUNCTUATION_REP if token[1] == PUNCTUATION else OPTIONAL_REP if token[1] == GAP else token[0]
        self.len_min = len(token[0])
        self.len_max = len(token[0])
        self.freq = int(token[2])
        self.punc_list = list()
        if token[1] == PUNCTUATION:
            self.punc_list.append(token[0].replace(' ', SPACE_REP))

    def update_pattern(self, new_token, tc):
        if self.element_type == GAP:
            self.regex = OPTIONAL_REP
        elif self.element_type == PUNCTUATION:
            self.regex = PUNCTUATION_REP
            if new_token[0].replace(' ', SPACE_REP) not in self.punc_list:
                self.punc_list.append(new_token[0].replace(' ', SPACE_REP))
        elif self.element_type in supported_type_rep.keys():
            self.regex = supported_type_rep[self.element_type]
        else:
            unknown_threshold = 0.8
            function_regex, unknown_ratio = tc.character_comp_regex(self.regex, new_token[0])
            if unknown_ratio > unknown_threshold:
                if self.element_type == ALPHA:
                    self.regex = ALPHA_REP
                elif self.element_type == ALPHANUM:
                    self.regex = ALPHANUM_REP
                elif self.element_type == DIGIT:
                    self.regex = DIGIT_REP
            else:
                self.regex = function_regex
        self.len_min = min(self.len_min, len(new_token[0]))
        self.len_max = max(self.len_max, len(new_token[0]))
        self.freq += int(new_token[2])

    def get_pattern(self):
        if self.element_type == PUNCTUATION:
            return '{}({})'.format(self.regex, ''.join(self.punc_list))
        elif self.element_type == GAP:
            return self.regex
        return '{}({}-{})'.format(self.regex, self.len_min, self.len_max)

    def get_type(self):
        return self.element_type

    def get_freq(self):
        return self.freq

    def get_min_max(self):
        return self.len_min, self.len_max
