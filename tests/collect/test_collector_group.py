# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for Group collector class"""

from openclean_pattern.collect.group import Group
from openclean_pattern.tokenize.regex import DefaultTokenizer


def test_group_align(business):
    """Tests the group align class """
    dt = DefaultTokenizer()
    encoded = dt.encode(business['Address '])

    ga = Group()
    aligned = ga.collect(encoded)

    assert list(aligned.keys()) == [7,9,11,5]
    assert len(aligned[7]) == 13
    assert len(aligned[9]) == 2
    assert len(aligned[11]) == 2
    assert len(aligned[5]) == 3