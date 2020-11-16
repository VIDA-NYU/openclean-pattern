# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for GroupAlign class"""

import pytest
from openclean_pattern.align.group import GroupAligner
from openclean_pattern.tokenize.regex import DefaultTokenizer


def test_group_align(business):

    """ensure group align groups same length tokens together"""
    dt = DefaultTokenizer()
    encoded = dt.encode(business['Address '])

    ga = GroupAligner()
    aligned = ga.align(encoded)

    assert list(aligned.keys()) == [7,9,11,5]
    assert len(aligned[7]) == 13
    assert len(aligned[9]) == 2
    assert len(aligned[11]) == 2
    assert len(aligned[5]) == 3