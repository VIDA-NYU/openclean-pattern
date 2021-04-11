# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import DefaultTypeResolver, GeoSpatialResolver, AddressDesignatorResolver
from openclean_pattern.tokenize.regex import RegexTokenizer

"""unit tests for geospatial resolvers"""

import pytest


def test_geospatial_resolver(business):
    gt = DefaultTypeResolver(interceptors=GeoSpatialResolver(levels=[0, 1, 2]))
    rt = RegexTokenizer(type_resolver=gt)

    test_data = [
        'united kingdom of great britain and northern ireland, 36 Georgia Street, islamic republic of pakistan Ave']
    encoded = rt.encode(test_data)[0]

    assert len(encoded) == 13
    assert encoded[0].regex_type == SupportedDataTypes.ADMIN_LEVEL_0
    assert encoded[1].regex_type == SupportedDataTypes.PUNCTUATION
    assert encoded[2].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[3].regex_type == SupportedDataTypes.DIGIT
    assert encoded[4].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[5].regex_type == SupportedDataTypes.ADMIN_LEVEL_0
    assert encoded[6].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[7].regex_type == SupportedDataTypes.ALPHA
    assert encoded[8].regex_type == SupportedDataTypes.PUNCTUATION
    assert encoded[9].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[10].regex_type == SupportedDataTypes.ADMIN_LEVEL_0
    assert encoded[11].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[12].regex_type == SupportedDataTypes.ALPHA


def test_multi_resolvers(business):
    """
    test multiple resolvers in series: AD -> GEO -> AT
    """
    deft = DefaultTypeResolver(interceptors=[AddressDesignatorResolver(), GeoSpatialResolver(levels=[0, 1, 2])])
    rt = RegexTokenizer(type_resolver=deft)

    test_data = [
        'united kingdom of great britain and northern ireland, Georgia Street, islamic republic of pakistan Ave',
        'January Ave. | Islamabad'
    ]
    encoded = rt.encode(test_data)

    assert encoded[0][0].regex_type == SupportedDataTypes.ADMIN_LEVEL_0
    assert encoded[0][1].regex_type == SupportedDataTypes.PUNCTUATION
    assert encoded[0][2].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[0][3].regex_type == SupportedDataTypes.ADMIN_LEVEL_0
    assert encoded[0][4].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[0][5].regex_type == SupportedDataTypes.STREET
    assert encoded[0][6].regex_type == SupportedDataTypes.PUNCTUATION
    assert encoded[0][7].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[0][8].regex_type == SupportedDataTypes.ADMIN_LEVEL_0
    assert encoded[0][9].regex_type == SupportedDataTypes.SPACE_REP
    assert encoded[0][10].regex_type == SupportedDataTypes.STREET


# commented because time consuming
def test_multi_resolvers_full(urban):
    """
        test multiple resolvers in series: AD -> GEO -> AT
        """
    deft = DefaultTypeResolver(interceptors=[AddressDesignatorResolver(), GeoSpatialResolver(levels=[0, 1, 2])])
    rt = RegexTokenizer(type_resolver=deft)

    encoded = rt.encode(urban)

    # group the column
    from openclean_pattern.collect.group import Group

    ga = Group()
    grouped = ga.collect(encoded)

    # compile the pattern
    from openclean_pattern.regex.compiler import DefaultRegexCompiler

    rws = DefaultRegexCompiler()
    compiled = rws.compile(encoded, grouped)

    assert len(compiled) == 14
    types = [[SupportedDataTypes.DIGIT, SupportedDataTypes.SPACE_REP, SupportedDataTypes.ALPHA, SupportedDataTypes.PUNCTUATION, SupportedDataTypes.SPACE_REP, SupportedDataTypes.SPACE_REP, SupportedDataTypes.ALPHA, SupportedDataTypes.PUNCTUATION,
              SupportedDataTypes.SPACE_REP, SupportedDataTypes.ALPHA, SupportedDataTypes.PUNCTUATION, SupportedDataTypes.SPACE_REP, SupportedDataTypes.DIGIT],
             [SupportedDataTypes.ALPHA, SupportedDataTypes.SPACE_REP, SupportedDataTypes.ALPHA, SupportedDataTypes.SPACE_REP, SupportedDataTypes.DIGIT, SupportedDataTypes.PUNCTUATION, SupportedDataTypes.SPACE_REP, SupportedDataTypes.SPACE_REP, SupportedDataTypes.ALPHA,
              SupportedDataTypes.PUNCTUATION, SupportedDataTypes.SPACE_REP, SupportedDataTypes.ALPHA, SupportedDataTypes.PUNCTUATION, SupportedDataTypes.SPACE_REP, SupportedDataTypes.DIGIT],
             [SupportedDataTypes.DIGIT, SupportedDataTypes.SPACE_REP, SupportedDataTypes.ALPHA, SupportedDataTypes.SPACE_REP, SupportedDataTypes.ALPHA, SupportedDataTypes.SPACE_REP, SupportedDataTypes.STREET, SupportedDataTypes.SPACE_REP, SupportedDataTypes.SUD,
              SupportedDataTypes.SPACE_REP, SupportedDataTypes.DIGIT, SupportedDataTypes.PUNCTUATION, SupportedDataTypes.SPACE_REP, SupportedDataTypes.SPACE_REP, SupportedDataTypes.ALPHA, SupportedDataTypes.SPACE_REP, SupportedDataTypes.STREET,
              SupportedDataTypes.PUNCTUATION, SupportedDataTypes.SPACE_REP, SupportedDataTypes.ADMIN_LEVEL_2, SupportedDataTypes.PUNCTUATION, SupportedDataTypes.SPACE_REP, SupportedDataTypes.DIGIT]]
    for i, t in zip([13, 15, 23], types):
        for element, truth in zip(list(compiled[i].values())[0].container, t):
            assert element.element_type == truth
