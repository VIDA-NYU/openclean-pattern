from openclean.regex.regex_objects import RegexToken, RegexRow, RegexMatrix
from openclean.regex.pattern_generator import RegexTokensPattern
from openclean import GAP_SYMBOL, NEW_HYPHEN_SYMBOL
from openclean.regex import *

import numpy as np, re
from pandas import isnull

MAX_INT = np.inf
MIN_INT = -np.inf

class RegexCompiler(object):
    def __init__(self, encoders=None):
        self.encoders = encoders

    @staticmethod
    def compile(aligned_rows, frequency_dict=None):
        '''
        Translates the aligned_rows to datatype representation.
        stringify allows to convert non aligned rows to Tokens too
        :param aligned_rows: rows
        :param freq: dict
        :return: regex matrix (list), stringified (list)
        '''

        matrix = list()
        stringified = list()

        for i, arow in enumerate(aligned_rows):
            if frequency_dict:
                try:
                    freq = frequency_dict[''.join(arow)]
                except Exception as e:
                    raise e # (''.join(arow) + ' not in frequency_dict')
            else:
                freq = 1

            regex_row = RegexRow(regex_row=list(), frequency=0)
            for j, token in enumerate(arow):
                regex_row.append(RegexToken.from_token(token, freq))
            regex_row.set_frequency(freq)
            matrix.append(regex_row)
            stringified.append(regex_row.get_info().split(' '))

        return matrix, stringified

    @staticmethod
    def encode_and_compile(rows, row_tokenizer, frequency_dict=None, supported_encoders=None):
        '''
        Translates the rows to regex_rows after encoding data supported types.
        :param rows: pd.Series - not tokenized
        :param frequency_dict: dict
        :param row_tokenizer: callback to tokenizer f()
        :param supported_encoders: list of supported datatype prefix tries
        :return: regex matrix (list), stringified (list)
        '''

        def lookup(val, dtype, freq):
            '''
            lookup in dtype prefix trie
            :param val: list - each row value
            :param dtype: trie object
            :return: lookedup and replaced row value
            '''
            if isinstance(val, str):
                val = [val]

            prefixes = list()
            for v in val:
                if isinstance(v, str):
                    prefixes.append(dtype.find_prefixes(v))  # gets all prefixes discovered from in a row
            prefixes = [item for sublist in prefixes for item in sublist]
            prefixes = sorted(prefixes, key=lambda x: len(x), reverse=True)

            p = 0
            a = val
            while p < len(prefixes):
                c = list()
                for ai in a:
                    if not isinstance(ai, RegexToken):
                        splits = re.split(r'(\b' + prefixes[p] + r'\b)', ai)
                        b = list()
                        for split in splits:
                            if split == prefixes[p]:
                                b.append(RegexToken(regex_type=dtype.get_label(split),
                                                    size=len(split),
                                                    token=split,
                                                    freq=freq))
                            else:
                                b.append(split)
                        c.append(b)
                    else:
                        c.append([ai])
                a = [item for sublist in c for item in sublist]
                p += 1

            return a

        matrix = list()
        stringified = list()

        for i, arow in enumerate(rows):
            try:
                freq = frequency_dict[arow] if frequency_dict else 1
            except Exception as e:
                raise e # (''.join(arow) + ' not in frequency_dict')

            regex_row = RegexRow(regex_row=list(),frequency=0)

            if supported_encoders:
                for se in supported_encoders:
                    arow = lookup(arow, se, freq)

            # split/tokenize remaining tokens
            for j, token in enumerate(arow):
                if isinstance(token, RegexToken):
                    regex_row.append(token)
                else:
                    for t in row_tokenizer(token):
                        regex_row.append(RegexToken.from_token(t, freq))
            regex_row.set_frequency(freq)

            matrix.append(regex_row)
            stringified.append(regex_row.get_info().split(' '))

        return matrix, stringified

    #todo: deprecate this
    @staticmethod
    def generate_regex(regex_matrix):
        full_regex = str()
        general_full_regex = str()

        for column_no in range(len(regex_matrix)):
            column = regex_matrix[:, column_no]
            column_tokens = np.array(list(set([c.get_token() if not isnull(c) else None for c in column])))
            column_regex = RegexTokensPattern()
            for token in column_tokens:
                try:
                    none_token = isnull(token[0])
                except Exception:
                    none_token = isnull(token)
                if none_token:
                    token = (GAP_SYMBOL, GAP, 1)
                column_regex.insert_token(token)
            fr, gfr = column_regex.condense()
            full_regex += fr + ' '
            general_full_regex += gfr + ' '
        return full_regex, general_full_regex

    @staticmethod
    def generate_regex_from_matrix(matrix):
        full_regex = str()
        general_full_regex = str()
        for col in range(matrix[0].get_size()):
            column_regex = RegexTokensPattern()
            for row in range(len(matrix)):
                token = matrix[row].get_regex_token(col).get_token()
                column_regex.insert_token(token)
            fr, gfr = column_regex.condense()
            full_regex += fr + ' '
            general_full_regex += gfr + ' '
        return full_regex, general_full_regex