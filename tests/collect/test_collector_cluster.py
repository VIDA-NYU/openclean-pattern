# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for Cluster class"""

from openclean_pattern.collect.cluster import Cluster
from openclean_pattern.tokenize.factory import DefaultTokenizer


def test_distance_ted_compute(business):
    rows = DefaultTokenizer().encode(business['Address '])

    aligned = Cluster(dist='TED', min_samples=3).collect(rows)

    assert len(business.loc[aligned[0],'Address ']) == 8

    results = ['4356 NE DAVIS ST', '2947 NE VILLAGE CT', '1754 ORCHARD HOME DR',
     '6740 NE PORTLAND HIGHWAY', '33555 NE KRAMIEN ROAD', '5290 SW CHESTNUT AVE',
     '3590 SE CHARTER PL', '18355 SHADY HOLLOW WAY']

    for i in business.loc[aligned[0], 'Address ']:
        assert i in results


def test_distance_absolute_compute(business):
    rows = DefaultTokenizer().encode(business['Address '])
    groups = Cluster(dist='ABS', min_samples=3).collect(rows)

    for group, idx in groups.items():
        # noise
        if group != -1:
            # all other rows should be grouped by no. of tokens
            leng = len(rows[idx[0]])
            for id in idx:
                assert len(rows[id]) == leng

