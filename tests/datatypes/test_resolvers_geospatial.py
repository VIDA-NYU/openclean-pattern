# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import DefaultTypeResolver, GeoSpatialResolver, AddressDesignatorResolver
from openclean_pattern.tokenize.regex import RegexTokenizer


"""unit tests for geospatial resolvers"""

import pytest


def test_geospatial_resolver(business):
    gt = DefaultTypeResolver(interceptors=GeoSpatialResolver(levels=[0,1,2]))
    rt = RegexTokenizer(type_resolver=gt)

    test_data = ['united kingdom of great britain and northern ireland, 36 Georgia Street, islamic republic of pakistan Ave']
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
        ['united kingdom of great britain and northern ireland, Georgia Street, islamic republic of pakistan Ave'],
        ['January Ave. | Islamabad']
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

def test_multi_resolvers_full():
        """
        test multiple resolvers in series: AD -> GEO -> AT
        """
        deft = DefaultTypeResolver(interceptors=[AddressDesignatorResolver(), GeoSpatialResolver(levels=[0, 1, 2])])
        rt = RegexTokenizer(type_resolver=deft)

        import pandas as pd
        test_data = pd.read_csv('/home/maqzi/PycharmProjects/openclean-pattern/resources/dev/urban.csv')
        geo = test_data[['Address ', 'Address Continued', 'City', 'State', 'Zip Code']]
        geo.loc[:, 'Full Address'] = test_data['Address '] + ',\n' + test_data['Address Continued'].fillna('') + '\n' + test_data[
            'City'] + ', ' + test_data['State'] + ', ' + test_data['Zip Code']

        encoded = rt.encode(geo['Full Address'].to_list())

        # align the column
        from openclean_pattern.align.group import GroupAligner

        ga = GroupAligner()
        aligned = ga.align(encoded)

        # compile the pattern
        from openclean_pattern.regex.compiler import DefaultRegexCompiler

        rws = DefaultRegexCompiler()
        compiled = rws.compile(encoded, aligned)

        assert len(compiled) == 24
        types = [['DIGIT', 'PUNCTUATION', 'SPACE_REP', 'SPACE_REP', 'ADMIN_LEVEL_1', 'PUNCTUATION', 'SPACE_REP', 'ALPHA', 'PUNCTUATION', 'SPACE_REP', 'DIGIT'],
                 ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'STREET', 'PUNCTUATION', 'SPACE_REP', 'SPACE_REP', 'ALPHA', 'PUNCTUATION', 'SPACE_REP', 'ALPHA', 'PUNCTUATION', 'SPACE_REP', 'DIGIT'],
                 ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'STREET', 'SPACE_REP', 'SUD', 'SPACE_REP', 'DIGIT', 'PUNCTUATION', 'SPACE_REP', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'STREET', 'PUNCTUATION', 'SPACE_REP', 'ALPHA', 'PUNCTUATION', 'SPACE_REP', 'DIGIT']]
        for i, t in zip([11, 15, 23], types):
            for element, truth in zip(compiled[i].container, t):
                assert element.element_type == truth
