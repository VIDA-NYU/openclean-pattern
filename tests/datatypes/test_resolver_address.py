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
    tokens = rt.tokens(business['Address_combined'].to_list()[2])
    # LN -> _STREET_
    # ['22207 SW SIR LANCELOT LN | nan'],
    assert tokens[0].regex_type == SupportedDataTypes.DIGIT
    assert tokens[1].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[2].regex_type == SupportedDataTypes.ALPHA
    assert tokens[3].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[4].regex_type == SupportedDataTypes.ALPHA
    assert tokens[5].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[6].regex_type == SupportedDataTypes.ALPHA
    assert tokens[7].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[8].regex_type == SupportedDataTypes.STREET
    assert tokens[9].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[10].regex_type == SupportedDataTypes.PUNCTUATION
    assert tokens[11].regex_type == SupportedDataTypes.SPACE_REP
    assert tokens[12].regex_type == SupportedDataTypes.ALPHA
