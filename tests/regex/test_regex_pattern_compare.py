# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""test pattern comparison with values"""

from openclean_pattern.regex.compiler import DefaultRegexCompiler
from openclean_pattern.opencleanpatternfinder import OpencleanPatternFinder

ROWS = [['32A West Broadway 10007'],
        ['54E East VillageA 10003']]


def test_regex_pattern_compare():
    """creates a pattern from ROWS[0] and compares it with ROWS[1]
   """
    pf = OpencleanPatternFinder(
        tokenizer='default',
        collector='group',
        compiler=DefaultRegexCompiler()
    )

    pattern = pf.find(series=ROWS[0])[7]

    match = ROWS[1]
    assert pattern.top(pattern=True).compare(value=match, tokenizer=pf.tokenizer)

    mismatch = '321-West Broadway 10007'
    assert not pattern.top(pattern=True).compare(value=mismatch, tokenizer=pf.tokenizer)


def test_regex_pattern_compile():
    """Tests a pattern using the Value Function
    """
    pf = OpencleanPatternFinder(
        tokenizer='default',
        collector='group',
        compiler=DefaultRegexCompiler()
    )

    pattern = pf.find(series=ROWS[0])[7]

    match = ROWS[1]
    assert pattern[pattern.top()].compile(tokenizer=pf.tokenizer).eval(match)

    mismatch = '321-West Broadway 10007'
    assert not pattern[pattern.top()].compile(tokenizer=pf.tokenizer).eval(mismatch)
