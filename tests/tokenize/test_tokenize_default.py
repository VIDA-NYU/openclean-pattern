# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.


from openclean_pattern.tokenize.regex import DefaultTokenizer, RegexTokenizer
from openclean_pattern.datatypes.base import SupportedDataTypes

"""Unit test for the default tokenizer"""

ROWS = ['273 W MERCER STREET', '12 E. BROADWAY']


def test_default_tokenizer_tokenize():
    dt = DefaultTokenizer()
    tokenized = dt.tokenize(ROWS)
    assert tokenized[0] == ('273', ' ', 'w', ' ', 'mercer', ' ', 'street')
    assert tokenized[1] == ('12', ' ', 'e', '.', ' ', 'broadway')


def test_default_tokenizer_encode():
    dt = DefaultTokenizer()
    encoded = dt.encode(ROWS)
    assert encoded[0][0].value == '273' and encoded[0][0].size == 3 and encoded[0][0].regex_type == SupportedDataTypes.DIGIT


