# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for the tree edit distance class"""

from openclean_pattern.align.distance.factory import DistanceFactory
from openclean_pattern.tokenize.factory import DefaultTokenizer


def test_distance_ted_compute(dates):
    test = '12TH JANUARY 2011'
    test_tokens = DefaultTokenizer().tokens(rowidx=0, value=test)
    train_tokens = DefaultTokenizer().encode(dates)

    dist = DistanceFactory.create('TED')
    distances = list()
    for row in train_tokens:
        distances.append(dist.compute(test_tokens, row))

    for i, j in zip(distances, [8/9, 8/9, 0.2, 0.8]):
        assert i == j
