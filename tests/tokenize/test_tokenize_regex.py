# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

from openclean_pattern.tokenize.regex import RegexTokenizer
from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import BasicTypeResolver

"""Unit test for the regex tokenizer"""

ROWS = ['273 W MERCER STREET', '12 E. BROADWAY']


def test_regex_tokenizer_tokenize():
    dt = RegexTokenizer()
    assert dt.tokens(ROWS[0]) == ['273', ' ', 'w', ' ', 'mercer', ' ', 'street']
    assert dt.tokens(ROWS[1]) == ['12', ' ', 'e', '.', ' ', 'broadway']


def test_regex_tokenizer_encode():
    dt = RegexTokenizer(type_resolver=BasicTypeResolver())
    encoded = dt.encode(ROWS)
    assert encoded[0][0].value == '273' and encoded[0][0].size == 3 and encoded[0][0].regex_type == SupportedDataTypes.DIGIT


# todo: different regex, abbreviations (tested in test_resolver_business)
