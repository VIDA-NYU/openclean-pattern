# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for DefaultRegexCompiler class"""

from openclean_pattern.regex.compiler import DefaultRegexCompiler
from openclean_pattern.tokenize.regex import DefaultTokenizer
from openclean_pattern.align.group import Group


def test_default_regex_compiler(business):
    compiler = DefaultRegexCompiler(per_group='top')
    tokenizer = DefaultTokenizer()
    collector = Group()

    tokenized = tokenizer.encode(business['Address '])
    groups = collector.collect(tokenized)

    patterns = compiler.compile(tokenized, groups)

    assert len(patterns) == 4
    types = [['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA'],
            ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA'],
            ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']]
    for i, t in zip([9, 5, 7], types):
        for element, truth in zip(patterns[i].top(pattern=True).container, t):
            assert element.element_type == truth


def test_default_regex_compiler_all(business):
    compiler = DefaultRegexCompiler(per_group='all')
    tokenizer = DefaultTokenizer()
    collector = Group()

    tokenized = tokenizer.encode(business['Address '])
    groups = collector.collect(tokenized)

    patterns = compiler.compile(tokenized, groups)

    assert len(patterns) == 4
    assert len(patterns[7]) == 4
    assert len(patterns[11]) == 2
    assert len(patterns[9]) == 1
    assert len(patterns[5]) == 2

    truth = [
        'DIGIT SPACE_REP ALPHANUM SPACE_REP ALPHA SPACE_REP ALPHA',
        'DIGIT SPACE_REP ALPHA SPACE_REP ALPHA SPACE_REP ALPHA',
        'DIGIT SPACE_REP ALPHA SPACE_REP ALPHANUM SPACE_REP ALPHA',
        'ALPHA SPACE_REP ALPHA SPACE_REP ALPHA SPACE_REP ALPHA'
    ]

    for t, key in zip(truth, patterns[7]):
        assert key == t

def test_default_regex_anomaly(business):
    compiler = DefaultRegexCompiler()
    tokenizer = DefaultTokenizer()
    collector = Group()

    tokenized = tokenizer.encode(business['Address '])
    groups = collector.collect(tokenized)

    patterns = compiler.compile(tokenized, groups)

    types = [['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA'],
             ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA'],
             ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']]
    for i, t in zip([9, 5, 7], types):
        for element, truth in zip(patterns[i].top(pattern=True).container, t):
            assert element.element_type == truth

    match_patterns = list()
    for pat in patterns.values():
        match_patterns.append(pat.top(pattern=True))

    mismatches = compiler.mismatches(tokenized, patterns=match_patterns)
    mismatched_rows = business.loc[mismatches, 'Address ']
    assert len(mismatched_rows) == 7 # except row#14, the other mismatches are e.g. those that had 14th (alphanum) instead of an alpha at position 2
    assert 14 in mismatched_rows.index # index # 14 = 'ATTN HEATHER J HANSEN' which shouldnt match the pattern.
