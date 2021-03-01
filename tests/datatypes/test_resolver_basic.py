# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for basic types resolver class"""

from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import BasicTypeResolver
from openclean_pattern.tokenize.regex import RegexTokenizer


def test_basic_resolver(dates):
    row = 0

    rt = RegexTokenizer()
    at = BasicTypeResolver()
    encoded = at.resolve_row(row, dates.iloc[row][0], rt._tokenize_value)

    # ["Monday, 21st March, 2019"],
    assert encoded[0].regex_type == SupportedDataTypes.ALPHA
    assert encoded[1].regex_type == SupportedDataTypes.PUNCTUATION
    assert encoded[2].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[3].regex_type == SupportedDataTypes.ALPHANUM
    assert encoded[4].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[5].regex_type == SupportedDataTypes.ALPHA
    assert encoded[6].regex_type == SupportedDataTypes.PUNCTUATION
    assert encoded[7].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[8].regex_type == SupportedDataTypes.DIGIT
