# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for business type resolver classs"""

from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import BusinessEntityResolver, DefaultTypeResolver
from openclean_pattern.tokenize.regex import RegexTokenizer


def test_default_be_resolver(business):
    dt = DefaultTypeResolver(interceptors=BusinessEntityResolver())
    rt = RegexTokenizer(type_resolver=dt)

    encoded = rt.encode(business['Business Name'].to_list())

    # ['TSHIRTS4TRUTH LLC'"],
    assert encoded[1][0].regex_type == SupportedDataTypes.ALPHANUM
    assert encoded[1][1].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[1][2].regex_type == SupportedDataTypes.BE


def test_default_be_resolver_abbreviations(business):
    dt = DefaultTypeResolver(interceptors=BusinessEntityResolver())

    # ['RO SHOW NETWORK L.L.C.']
    # without abbreviation parsing
    rt = RegexTokenizer(type_resolver=dt)
    encoded = rt.encode(business['Business Name'].to_list())

    assert len(encoded[12]) == 12  # l.l.c. will broken down into separate tokens
    assert encoded[12][0].regex_type == SupportedDataTypes.ALPHA
    assert encoded[12][1].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[12][2].regex_type == SupportedDataTypes.ALPHA
    assert encoded[12][3].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[12][4].regex_type == SupportedDataTypes.ALPHA
    assert encoded[12][5].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[12][6].regex_type == SupportedDataTypes.ALPHA
    assert encoded[12][7].regex_type == SupportedDataTypes.PUNCTUATION
    assert encoded[12][8].regex_type == SupportedDataTypes.ALPHA
    assert encoded[12][9].regex_type == SupportedDataTypes.PUNCTUATION
    assert encoded[12][10].regex_type == SupportedDataTypes.ALPHA
    assert encoded[12][11].regex_type == SupportedDataTypes.PUNCTUATION

    # with abbreviations parsing
    rt = RegexTokenizer(abbreviations=True, type_resolver=dt)
    encoded = rt.encode(business['Business Name'].to_list())

    assert len(encoded[12]) == 7  # l.l.c. => llc => BE
    assert encoded[12][0].regex_type == SupportedDataTypes.ALPHA
    assert encoded[12][1].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[12][2].regex_type == SupportedDataTypes.ALPHA
    assert encoded[12][3].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[12][4].regex_type == SupportedDataTypes.ALPHA
    assert encoded[12][5].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[12][6].regex_type == SupportedDataTypes.BE

