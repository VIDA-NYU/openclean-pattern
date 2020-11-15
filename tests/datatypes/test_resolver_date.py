# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for datetype resolver classs"""

from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import DateResolver
from openclean_pattern.tokenize.regex import RegexTokenizer


def test_datetype_resolver(dates):
    dt = DateResolver()

    # a tokenizer that only detects compound dates not atomic
    rt = RegexTokenizer(type_resolver=dt)
    encoded = rt.encode(dates.to_list())

    # ["Monday, 21st March, 2019"],
    assert encoded[0][0].regex_type == SupportedDataTypes.WEEKDAY
    assert encoded[0][1] == ','
    assert encoded[0][2] == ' '
    assert encoded[0][3] == '21st'
    assert encoded[0][4] == ' '
    assert encoded[0][5].regex_type == SupportedDataTypes.MONTH
    assert encoded[0][6] == ','
    assert encoded[0][7] == ' '
    assert encoded[0][8] == '2019'
