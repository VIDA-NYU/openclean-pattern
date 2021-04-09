# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for business type resolver classs"""

from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import BusinessEntityResolver, DefaultTypeResolver
from openclean_pattern.tokenize.regex import RegexTokenizer


def test_default_be_resolver(business):
    dt = DefaultTypeResolver(interceptors=BusinessEntityResolver())
    rt = RegexTokenizer(type_resolver=dt)

    tokens = rt.tokens(business['Business Name'].to_list()[1])

    # ['TSHIRTS4TRUTH LLC'"],
    assert tokens[0].regex_type == SupportedDataTypes.ALPHANUM
    assert tokens[1].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[2].regex_type == SupportedDataTypes.BE


def test_default_be_resolver_abbreviations(business):
    dt = DefaultTypeResolver(interceptors=BusinessEntityResolver())

    # ['RO SHOW NETWORK L.L.C.']
    # without abbreviation parsing
    rt = RegexTokenizer(type_resolver=dt)
    tokens = rt.tokens(business['Business Name'].to_list()[12])

    assert len(tokens) == 12  # l.l.c. will broken down into separate tokens
    assert tokens[0].regex_type == SupportedDataTypes.ALPHA
    assert tokens[1].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[2].regex_type == SupportedDataTypes.ALPHA
    assert tokens[3].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[4].regex_type == SupportedDataTypes.ALPHA
    assert tokens[5].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[6].regex_type == SupportedDataTypes.ALPHA
    assert tokens[7].regex_type == SupportedDataTypes.PUNCTUATION
    assert tokens[8].regex_type == SupportedDataTypes.ALPHA
    assert tokens[9].regex_type == SupportedDataTypes.PUNCTUATION
    assert tokens[10].regex_type == SupportedDataTypes.ALPHA
    assert tokens[11].regex_type == SupportedDataTypes.PUNCTUATION

    # with abbreviations parsing
    rt = RegexTokenizer(abbreviations=True, type_resolver=dt)
    tokens = rt.tokens(business['Business Name'].to_list()[12])

    assert len(tokens) == 7  # l.l.c. => llc => BE
    assert tokens[0].regex_type == SupportedDataTypes.ALPHA
    assert tokens[1].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[2].regex_type == SupportedDataTypes.ALPHA
    assert tokens[3].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[4].regex_type == SupportedDataTypes.ALPHA
    assert tokens[5].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[6].regex_type == SupportedDataTypes.BE
