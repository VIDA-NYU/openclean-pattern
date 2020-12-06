# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for Pad class"""

# todo: add test cases here
# todo: test optional pattern compilation

from openclean_pattern.align.pad import Padder
from openclean_pattern.align.cluster import Cluster
from openclean_pattern.tokenize.factory import DefaultTokenizer
from openclean_pattern.regex.compiler import DefaultRegexCompiler

from openclean.profiling.pattern import OpencleanPatternFinder


def test_padder_align(business):
    rows = DefaultTokenizer().encode(business['Address '])

    groups = Cluster(dist='TED', min_samples=3).collect(rows)
    padded_tokens = Padder().align(rows, groups)

    for group, idx in groups.items():
        leng = len(padded_tokens[idx[0]])
        for id in idx:
            assert len(padded_tokens[id]) == leng


def test_padder_regex_col_compile(business):
    dt = DefaultTokenizer()
    rows = dt.encode(business['Address '])

    cr = Cluster(dist='TED', min_samples=3)
    groups = cr.collect(rows)

    ar = Padder()
    padded_tokens = ar.align(rows, groups)

    cp = DefaultRegexCompiler(method='col')
    patterns = cp.compile(padded_tokens, groups)

    pf = OpencleanPatternFinder(
        tokenizer=dt,
        collector=cr,
        aligner=ar,
        compiler=cp
    )

    for k, pat in patterns.items():
        if k != -1: #ignore noise group for dbscan
            for value in business.loc[patterns[k].idx, 'Address ']:
                assert pat.compare(value, pf)


def test_padder_regex_row_compile(business):
    dt = DefaultTokenizer()
    rows = dt.encode(business['Address '])

    cr = Cluster(dist='TED', min_samples=3)
    groups = cr.collect(rows)

    ar = Padder()
    padded_tokens = ar.align(rows, groups)

    cp = DefaultRegexCompiler(method='row')
    patterns = cp.compile(padded_tokens, groups)

    pf = OpencleanPatternFinder(
        tokenizer=dt,
        collector=cr,
        aligner=ar,
        compiler=cp
    )

    for k, pat in patterns.items():
        if k != -1: #ignore noise group for dbscan
            for value in business.loc[patterns[k].idx, 'Address ']:
                assert pat.compare(value, pf)