# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for default resolver classs"""


from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import DateResolver, DefaultTypeResolver
from openclean_pattern.tokenize.regex import RegexTokenizer


def test_default_resolver_with_interceptor(dates):
    dt = DateResolver()

    # create a Regex Tokenizer object that does both basic and non-basic date type resolution
    rt = RegexTokenizer(
        type_resolver=DefaultTypeResolver(
            interceptors=dt
        )
    )
    tokens = rt.tokens(dates.to_list()[0])

    # ["Monday, 21st March, 2019"],
    assert tokens[0].regex_type == SupportedDataTypes.WEEKDAY
    assert tokens[1].regex_type == SupportedDataTypes.PUNCTUATION
    assert tokens[2].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[3].regex_type == SupportedDataTypes.ALPHANUM
    assert tokens[4].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[5].regex_type == SupportedDataTypes.MONTH
    assert tokens[6].regex_type == SupportedDataTypes.PUNCTUATION
    assert tokens[7].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[8].regex_type == SupportedDataTypes.DIGIT
