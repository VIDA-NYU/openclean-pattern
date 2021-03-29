# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for address type resolver classs"""

from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import AddressDesignatorResolver, DefaultTypeResolver
from openclean_pattern.tokenize.regex import RegexTokenizer


def test_default_ad_resolver(business):
    dt = DefaultTypeResolver(interceptors=AddressDesignatorResolver())
    rt = RegexTokenizer(type_resolver=dt)

    business['Address_combined'] = business['Address '].astype(str) + ' | ' + business['Address Continued'].astype(str)
    encoded = rt.encode(business['Address_combined'].to_list())
    # LN -> _STREET_
    # ['22207 SW SIR LANCELOT LN | nan'],
    assert encoded[2][0].regex_type == SupportedDataTypes.DIGIT
    assert encoded[2][1].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[2][2].regex_type == SupportedDataTypes.ALPHA
    assert encoded[2][3].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[2][4].regex_type == SupportedDataTypes.ALPHA
    assert encoded[2][5].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[2][6].regex_type == SupportedDataTypes.ALPHA
    assert encoded[2][7].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[2][8].regex_type == SupportedDataTypes.STREET
    assert encoded[2][9].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[2][10].regex_type == SupportedDataTypes.PUNCTUATION
    assert encoded[2][11].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[2][12].regex_type == SupportedDataTypes.ALPHA
