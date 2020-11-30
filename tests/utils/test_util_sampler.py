# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for the sampler class"""

from openclean_pattern.utils.utils import RandomSampler, WeightedRandomSampler, Distinct
from collections import Counter

DICT_DATA = {
    '3 GOLD ST': 90,
    '2 MERCER ST': 70,
    '1 BLEECKER ST': 50,
    '0 JAY ST': 30
}

LIST_DATA = [
    '3 GOLD ST', '3 GOLD ST', '3 GOLD ST', '3 GOLD ST', '3 GOLD ST', '3 GOLD ST', '3 GOLD ST', '3 GOLD ST', '3 GOLD ST',
    '2 MERCER ST', '2 MERCER ST', '2 MERCER ST', '2 MERCER ST', '2 MERCER ST', '2 MERCER ST', '2 MERCER ST',
    '1 BLEECKER ST', '1 BLEECKER ST', '1 BLEECKER ST', '1 BLEECKER ST', '1 BLEECKER ST',
    '0 JAY ST', '0 JAY ST', '0 JAY ST'
]


def test_weighted_random_sampler():
    sampler = WeightedRandomSampler(weights=Counter(DICT_DATA), n=.1, random_state=42)
    sample = sampler.sample()

    assert len(sample) == 24 # test n = 10%

    sampled = Counter(sample)
    assert len(sampled.keys()) == 4 # no extra data
    assert sampled['3 GOLD ST'] == 12
    assert sampled['2 MERCER ST'] == 6
    assert sampled['1 BLEECKER ST'] == 5
    assert sampled['0 JAY ST'] == 1


def test_random_sampler():
    sampler = RandomSampler(iterable=LIST_DATA, n=5, random_state=42)
    sample = sampler.sample()

    assert len(sample) == 5 # test n = 10%

    sampled = Counter(sample)
    assert len(sampled.keys()) == 3 # with equal weighing at this random state, '2 MERCER ST' doesnt get selected
    assert sampled['3 GOLD ST'] == 3
    assert sampled['2 MERCER ST'] == 0
    assert sampled['1 BLEECKER ST'] == 1
    assert sampled['0 JAY ST'] == 1

def test_distinct_sampler():
    sampler = Distinct(iterable=LIST_DATA)
    sample = sampler.sample()
    sampled = Counter(sample)

    assert len(sampled.keys()) == 4
    assert sampled['3 GOLD ST'] == 1
    assert sampled['2 MERCER ST'] == 1
    assert sampled['1 BLEECKER ST'] == 1
    assert sampled['0 JAY ST'] == 1
