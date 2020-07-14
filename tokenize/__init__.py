from openclean import GAP_SYMBOL, NEW_HYPHEN_SYMBOL
from abc import ABCMeta, abstractmethod

import pandas as pd

TOKENIZER_SMART = 'smart'
TOKENIZER_REGEX = 'punc'

TOKENIZERS = [TOKENIZER_REGEX, TOKENIZER_SMART]

class Tokenizer(object, metaclass=ABCMeta):
    def __init__(self, tokenizer_type):
        if tokenizer_type not in TOKENIZERS:
            raise NotImplementedError(tokenizer_type)
        self.tokenizer_type = tokenizer_type

    @staticmethod
    def replace_hyphens(column):
        assert isinstance(column, pd.Series)
        return column
        # return column.str.replace(GAP_SYMBOL, NEW_HYPHEN_SYMBOL) # legacy version GAP char replacement

    @staticmethod
    def replace_hyphens_row(x):
        assert isinstance(x, str)
        return x
        # return x.replace(GAP_SYMBOL, NEW_HYPHEN_SYMBOL) # legacy version GAP char replacement


    @abstractmethod
    def tokenize(self, column):
        '''
        tokenizes the column
        :param column: list
        :return: list of lists
        '''
        raise NotImplementedError()

    @abstractmethod
    def encode(self, column, freq):
        '''
        returns an encoded regex matrix and it's stringified version
        :param column: list
        :param freq: dict of frequencies
        :return: list of RegexRows, list of strings
        '''