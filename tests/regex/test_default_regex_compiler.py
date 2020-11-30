# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for DefaultRegexCompiler class"""

from openclean_pattern.regex.compiler import DefaultRegexCompiler
from openclean_pattern.tokenize.regex import DefaultTokenizer
from openclean_pattern.align.group import GroupAligner


def test_default_regex_compiler(business):
    compiler = DefaultRegexCompiler()
    tokenizer = DefaultTokenizer()
    aligner = GroupAligner()

    tokenized = tokenizer.encode(business['Address '])
    alignments = aligner.align(tokenized)

    patterns = compiler.compile(tokenized, alignments)

    assert len(patterns) == 4
    types = [['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA'],
            ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA'],
            ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']]
    for i, t in zip([9, 5, 7], types):
        for element, truth in zip(patterns[i].container, t):
            assert element.element_type == truth


def test_default_regex_anomaly(business):
    compiler = DefaultRegexCompiler()
    tokenizer = DefaultTokenizer()
    aligner = GroupAligner()

    tokenized = tokenizer.encode(business['Address '])
    alignments = aligner.align(tokenized)

    pattern = compiler.compile(tokenized, alignments)
    anomalies = compiler.anomalies(tokenized, alignments)

    types = [['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA'],
             ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA'],
             ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']]
    for i, t in zip([9, 5, 7], types):
        for element, truth in zip(pattern[i].container, t):
            assert element.element_type == truth

    assert len(anomalies[7]) == 5 # except row#14, the other mismatches are e.g. those that had 14th (alphanum) instead of an alpha at position 2
    assert 14 in anomalies[7] # index # 14 = 'ATTN HEATHER J HANSEN' which shouldnt match the pattern.
