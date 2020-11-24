# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for the PatternFinder Class"""

from openclean_pattern.patternfinder import PatternFinder
from openclean_pattern.regex.base import DefaultRegexCompiler, RowWiseCompiler

import pytest

def test_patternfinder_find(business):
    pf = PatternFinder(
        series=business['Address '],
        tokenizer='default',
        aligner='group',
        compiler=RowWiseCompiler()
    )

    patterns = pf.find()
    assert len(patterns) == 3

    types = ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']
    for elements, type in zip(patterns[9], types):
        assert elements.element_type == type

    pf = PatternFinder(
        series=business['Address '],
        tokenizer='default',
        aligner='group',
        compiler=DefaultRegexCompiler()
    )

    patterns = pf.find()
    assert len(patterns) == 3

    types = ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']
    for elements, type in zip(patterns[9], types):
        assert elements == type