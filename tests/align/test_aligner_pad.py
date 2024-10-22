# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for Pad class"""


from openclean_pattern.align.pad import Padder
from openclean_pattern.collect.cluster import Cluster
from openclean_pattern.tokenize.factory import DefaultTokenizer, RegexTokenizer
from openclean_pattern.datatypes.resolver import AddressDesignatorResolver, DefaultTypeResolver
from openclean_pattern.regex.compiler import DefaultRegexCompiler


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

    for k, pat in patterns.items():
        if k != -1:  # ignore noise group for dbscan
            for value in business.loc[pat.top(pattern=True).idx, 'Address ']:
                assert pat.top(pattern=True).compare(value, dt)


def test_padder_regex_row_compile(business):
    dt = DefaultTokenizer()
    rows = dt.encode(business['Address '])

    cr = Cluster(dist='TED', min_samples=3)
    groups = cr.collect(rows)

    ar = Padder()
    padded_tokens = ar.align(rows, groups)

    cp = DefaultRegexCompiler(method='row')
    patterns = cp.compile(padded_tokens, groups)

    for k, pat in patterns.items():
        if k != -1:  # ignore noise group for dbscan
            for value in business.loc[patterns[k].top(pattern=True).idx, 'Address ']:
                assert pat.top(pattern=True).compare(value, dt)


def test_padder_regex_typeresolver_col_compile(business):
    tr = DefaultTypeResolver(interceptors=[AddressDesignatorResolver()])
    dt = RegexTokenizer(type_resolver=tr)
    rows = dt.encode(business['Address '])

    cr = Cluster(dist='TED', min_samples=3)
    groups = cr.collect(rows)

    ar = Padder()
    padded_tokens = ar.align(rows, groups)

    cp = DefaultRegexCompiler(method='col')
    patterns = cp.compile(padded_tokens, groups)

    for k, pat in patterns.items():
        if k != -1:  # ignore noise group for dbscan
            for value in business.loc[patterns[k].top(pattern=True).idx, 'Address ']:
                assert pat.top(pattern=True).compare(value, dt)


def test_padder_regex_typeresolver_row_compile(business):
    tr = DefaultTypeResolver(interceptors=[AddressDesignatorResolver()])
    dt = RegexTokenizer(type_resolver=tr)
    rows = dt.encode(business['Address '])

    cr = Cluster(dist='TED', min_samples=3)
    groups = cr.collect(rows)

    ar = Padder()
    padded_tokens = ar.align(rows, groups)

    cp = DefaultRegexCompiler(method='row')
    patterns = cp.compile(padded_tokens, groups)

    for k, pat in patterns.items():
        if k != -1:  # ignore noise group for dbscan
            for value in business.loc[patterns[k].top(pattern=True).idx, 'Address ']:
                assert pat.top(pattern=True).compare(value, dt)
