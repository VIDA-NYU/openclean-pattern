# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for neigbor joining collector class"""

from openclean_pattern.collect.neighbor import NeighborJoin
from openclean_pattern.tokenize.factory import DefaultTokenizer
from openclean_pattern.datatypes.base import SupportedDataTypes

ADDRESSES = ['123 ST', '21W.AVENUE', 'WEST ALLEN 12']


def test_neighborjoining_distance():
    addresses = ADDRESSES[:2]

    dt = DefaultTokenizer()
    encoded = dt.encode(addresses)

    nj = NeighborJoin()
    dists = nj._compute_pairwise_distance(encoded)

    assert len(dists) == 2
    assert (dists == [[0, 0], [0, 0]]).all()


def test_neighborjoining_order():
    dt = DefaultTokenizer()
    encoded = dt.encode(ADDRESSES)

    nj = NeighborJoin()
    aln, order = nj.get_tree_and_order(encoded)

    actual = [SupportedDataTypes.ALPHANUM, SupportedDataTypes.PUNCTUATION, SupportedDataTypes.ALPHA]
    for i, o in enumerate(order[0][0][0]):
        assert o.regex_type == actual[i]


def test_neighborjoining_collect():
    dt = DefaultTokenizer()
    encoded = dt.encode(ADDRESSES)

    nj = NeighborJoin()
    order = nj.collect(encoded)

    actual = [1, 0, 2]
    for i, o in enumerate(order[0][0][0]):
        assert o == actual[i]
