# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the prefix tree data structure for token sequence lookup."""

import pytest

from openclean.function.token.base import Token
from openclean_pattern.tokenize.prefix_tree import PrefixTree


@pytest.mark.parametrize(
    'sequence,result',
    [
        ([Token('new'), Token('York'), Token('State')], 1),
        ([Token('new'), Token('York'), Token('city')], 2),
        ([Token('Boston')], 0),
        ([Token('new'), Token('England')], None),
        ([Token('14'), Token('th'), Token('St')], None),
        ([Token('St'), Token('Boston'), Token('MA')], 0)
    ]
)
def test_prefix_tree_lookup(sequence, result):
    """Test prefix tree lookup for a sequence of tokens."""
    pt = PrefixTree(vocabulary=[(['New York', 'New York City', 'Boston', 'New Brunswick', 'St'], 'TEST')])
    index, label = pt.prefix_search(content_words=sequence)
    assert index == result
    expected_label = 'TEST' if result is not None else None
    assert label == expected_label
