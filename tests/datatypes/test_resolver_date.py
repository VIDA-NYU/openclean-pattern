# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for datetype resolver classs"""

from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import DateResolver
from openclean_pattern.tokenize.regex import RegexTokenizer


def test_datetype_resolver(dates):
    dt = DateResolver()

    # a tokenizer that only detects non-basic dates not basic
    rt = RegexTokenizer(type_resolver=dt)
    tokens = rt.tokens(dates.to_list()[0])

    # ["Monday, 21st March, 2019"],
    assert tokens[0].regex_type == SupportedDataTypes.WEEKDAY
    assert tokens[1] == ','
    assert tokens[2] == ' '
    assert tokens[3] == '21st'
    assert tokens[4] == ' '
    assert tokens[5].regex_type == SupportedDataTypes.MONTH
    assert tokens[6] == ','
    assert tokens[7] == ' '
    assert tokens[8] == '2019'
