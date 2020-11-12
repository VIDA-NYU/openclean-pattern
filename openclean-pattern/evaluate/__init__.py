from openclean import GAP_SYMBOL, NEW_HYPHEN_SYMBOL
from openclean.regex import supported_type_rep, GAP, DIGIT, ALPHA, ALPHANUM, PUNCTUATION
from openclean.regex.pattern_generator import RegexTokensPattern
from openclean.tokenize.smart import SmartTokenizer
from openclean.regex.regex_objects import RegexRow, RegexToken

import pandas as pd, re
from pandas import isnull


class Evaluator(object):
    def __init__(self):
        pass

    @staticmethod
    def evaluate_matrix(regex_matrix, patterns):
        match_proportion = dict()
        try:
            if not isnull(patterns) and isinstance(patterns, dict):
                rtp = RegexTokensPattern()
                for pat in patterns:
                    freq = 0
                    matched = 0
                    for row in regex_matrix:
                        freq += row.frequency
                        if len(patterns[pat]) == row.get_size():
                            if rtp.compare_pattern_to_token(patterns[pat], row.get_all_tokens()):
                                matched += row.frequency
                    match_proportion[pat] = matched / freq
        except Exception as e:
            print("error in pat {} :: {} :: for row {} ".format(pat, patterns[pat], str(row.get_all_tokens())))
            raise TypeError("Incorrect evaluation patterns type")
        return match_proportion

    @staticmethod
    def evaluate_tokens(aligned_rows, frequency_dict, patterns):
        # takes in an nXm matrix with one token per column
        regex_matrix = list()  # np.empty(aligned_rows.shape, dtype=Regex_Token)
        freq = 1
        for i, arow in enumerate(aligned_rows):
            regex_row = RegexRow(regex_row=list(), frequency=0)
            if frequency_dict:
                try:
                    if len(arow) == 1:
                        freq = frequency_dict[arow[0]]
                    else:
                        freq = frequency_dict[''.join(arow)]
                except Exception as e:
                    raise e

            for j, token in enumerate(arow):
                if not isnull(token):
                    if token == GAP_SYMBOL:
                        type = GAP
                    elif token in supported_type_rep.keys():
                        type = supported_type_rep[token]
                    elif token.isdigit():
                        type = DIGIT
                    elif token.isalpha():
                        type = ALPHA
                    elif token.isalnum():
                        type = ALPHANUM
                    else:
                        type = PUNCTUATION

                    # converting to regex token important cause that returns HYPHEN_SYMBOL back to '-'
                    regex_row.append(RegexToken(regex_type=type, size=len(token), token=token, freq=freq))
            regex_row.set_frequency(freq)
            regex_matrix.append(regex_row)

        return Evaluator.evaluate_matrix(regex_matrix, patterns)