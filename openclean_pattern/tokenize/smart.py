from openclean_pattern import datatypes
from openclean_pattern.tokenize.base import Tokenizer
from openclean_pattern.tokenize.regex import RegexTokenizer
from openclean_pattern.regex.compiler import RegexCompiler

import re

TOKENIZER_SMART = 'smart'

class SmartTokenizer(Tokenizer):


# class SmartTokenizer(Tokenizer):
#     def __init__(self):
#         super(SmartTokenizer, self).__init__(TOKENIZER_SMART)
#         self.gs = datatypes.GeoSpatial()
#         self.dt = datatypes.DateTime()
#         self.be = datatypes.BusinessEntity()
#         self.ad = datatypes.AddressDesignator()
#         self.encoders = [self.gs, self.dt, self.be, self.ad]
#
#     def lookup(self, val):
#         '''
#         lookup in all prefix tries
#         :param val: each row value
#         :return: lookedup and fully replaced row value
#         '''
#         val = self.lookup_type(val, self.gs)
#         val = self.lookup_type(val, self.dt)
#         val = self.lookup_type(val, self.be)
#         val = self.lookup_type(val, self.ad)
#         return val
#
#     def lookup_type(self, val, dtype):
#         '''
#         lookup in dtype prefix trie
#         :param val: string - each row value
#         :param dtype: trie object
#         :return: lookedup and replaced row value
#         '''
#         prefixes = sorted(dtype.find_prefixes(val), key=lambda x: len(x), reverse=True)# gets all prefixes discovered from in a row
#         for p in prefixes:
#             val = re.sub(r'\b'+p+r'\b', dtype.get_label(p), val)
#         return val
#
#     def tokenize_value(self, x):
#         '''
#         split a string
#         :param x: string
#         :return: list of tokens
#         '''
#         return RegexTokenizer().tokenize_value(x)
#
#     def encode(self, column, freq):
#         '''
#         encodes and tokenizes the input column
#         :param column: pd.Series
#         :param freq: dict of frequencies
#         :return: list of RegexRows and list of strings
#         '''
#         return RegexCompiler.encode_and_compile(rows=column.tolist(), frequency_dict=freq, row_tokenizer=self.tokenize_row, supported_encoders=self.encoders)


# # todo: account for <apostrophe 's> similarly
# # split on everything except dots if abbreviations = True
# regex = r'[\w.]+' if abbreviations else r'[\w]+'
# content_words = re.findall(regex, content)
# content_words = [item for sublist in [j.split('_') for j in content_words] for item in
#                  sublist]  # handle _ separately