# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

from openclean_pattern.function.value import IsMatch, IsNotMatch
from openclean_pattern.opencleanpatternfinder import OpencleanPatternFinder
from openclean_pattern.regex.compiler import DefaultRegexCompiler

ROWS = [['32A West Broadway 10007'],
        ['54E East Village 10003']]


def test_func_match():
    """Test functionality of the match operator."""

    pf = OpencleanPatternFinder(
        tokenizer='default',
        aligner='group',
        compiler=DefaultRegexCompiler()
    )

    pattern = pf.find(series=ROWS[0])[7]

    match = ROWS[1][0]
    mismatch = '321-West Broadway 10007'

    # -- IsMatch --------------------------------------------------------------
    f = IsMatch(func=pattern.compare, generator=pf)
    assert f(match)
    assert not f(mismatch)

    # -- IsNotMatch -----------------------------------------------------------
    f = IsNotMatch(func=pattern.compare, generator=pf)
    assert not f(match)
    assert f(mismatch)
