from openclean import NEW_HYPHEN_SYMBOL, GAP_SYMBOL
from openclean.regex import supported_type_rep, DIGIT, ALPHANUM, PUNCTUATION, ALPHA, GAP

import numpy as np
from pandas import isnull
import re

class RegexToken:
    '''
    internal representation of each token with key information intact
    '''
    def __init__(self, regex_type, size, token, freq=1, regex_format=None):
        self.regex_type = regex_type
        self.size = int(size)
        self.token = token if token != NEW_HYPHEN_SYMBOL else GAP_SYMBOL
        self.regex_format = regex_format # todo: e.g. case information / num format
        self.freq = int(freq)

    def __repr__(self):
        return f'RegexToken({self.regex_type!r},{self.size!r},{self.token!r}, {self.freq!r})'

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.regex_type == other.regex_type \
               and self.size == other.size \
               and self.token == other.token \
               and self.regex_format == other.regex_format \
               and self.freq == other.freq

    @staticmethod
    def from_token(token, freq):
        if not isnull(token):
            # if token == GAP_SYMBOL:
            #     type = GAP
            if token in supported_type_rep.keys():
                type = supported_type_rep[token]
            elif token.isdigit():
                type = DIGIT
            elif token.isalpha():
                type = ALPHA
            elif token.isalnum():
                type = ALPHANUM
            else:
                type = PUNCTUATION
        return RegexToken(regex_type=type, token=token, size=len(token), freq=freq)

    def get_info(self):
        '''
        get token string representation
        :return: e.g. ALPHA(5) -> TYPE(TOKEN, SIZE, FREQUENCY)
        '''
        # return "{}({},{},{})".format(self.regex_type, self.token, self.size, self.freq)
        return str(self)

    def get_type(self):
        return self.regex_type

    def get_size(self):
        return self.size

    # todo: switch with get_token_str
    def get_token(self):
        return tuple([self.token, self.regex_type, self.freq])

    def get_token_str(self):
        return self.token

    def get_regex_token(self):
        return self

    def get_frequency(self):
        return self.freq

# delegate list
from itertools import islice
class RegexRow:
    '''
    RegexRow representation
    # todo: update Compiler:compile and Compiler:generate_regex to support this
    '''
    def __init__(self, regex_row=list(), frequency=0):
        for tok in regex_row:
            if not isinstance(tok, RegexToken):
                raise ValueError('all list items should be RegexTokens')
        self.regex_row = regex_row
        self.frequency = frequency

    def __repr__(self):
        return f'{self.__class__.__name__}({self.regex_row!r}, {self.frequency!r})'

    def __len__(self):
        return len(self.regex_row)

    def __iter__(self):
        return iter(self.regex_row)

    def __getitem__(self, item):
        if isinstance(item, int) and item >= 0:
            return list(islice(self.regex_row, item, item+1))
        elif isinstance(item, slice):
            return list(islice(self.regex_row, item.start, item.stop, item.step))
        else:
            raise KeyError("Key must be non negative integer or slice, not {}".format(item))

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.regex_row == other.regex_row and self.frequency == other.frequency

    def append(self, item):
        if self.is_valid_token(item):
            self.regex_row.append(item)
        else:
            raise TypeError("Invalid input item. Regex Row only accepts Regex Tokens")

    def is_valid_token(self, token):
        # if 'regex_type' in token and 'size' in token and 'token' in token:
        if isinstance(token, RegexToken):
            return True
        return False

    def remove(self, item):
        self.regex_row.remove(item)

    def get_info(self):
        tokens = [token.get_info() for token in self.regex_row]
        return ' '.join(tokens)

    def get_regex_token(self, index):
        return self.regex_row[index].get_regex_token()

    def get_all_tokens(self):
        tokens = list()
        for tok in self.regex_row:
            tokens.append(tok.get_token())
        return tokens

    def get_all_regex_tokens(self):
        tokens = list()
        for tok in self.regex_row:
            tokens.append(tok.get_regex_token())
        return tokens

    def get_size(self):
        return len(self.regex_row)

    def set_frequency(self, frequency):
        self.frequency = frequency

    @staticmethod
    def create_row(u):
        '''
        creates a regexrow object from a list of RegexToken.get_info() strings
        :param u: list of RegexToken.get_info()
        :return: RegexRow()
        '''
        urow = RegexRow()
        for ui in u:
            if ui == '-':
                #todo: handle commas
                urow.append(RegexToken(regex_type=GAP, token=GAP_SYMBOL, size=1, freq=1))
            else:
                type, token, size, freq = re.findall(r'(.*?)\((.*?),(.*?),(.*?)\)', ui)[0]
                urow.append(RegexToken(regex_type=type, token=token, size=int(size), freq=int(freq)))
        urow.set_frequency(frequency=freq)
        return urow

class RegexMatrix:
    '''
    Entire RegexMatrix representation
    todo: is this even worth it?
    '''
    def __init__(self, rows):
        self.matrix = np.array([rows], dtype=RegexRow)


class RegexSerializer(object):
    '''
    to serialize RegexTokens (for now)
    '''
    def __init__(self):
        pass

    def serialize(self, regex_matrix):
        pass