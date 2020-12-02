# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for the PatternFinder Class"""

from openclean_pattern.patternfinder import PatternFinder
from openclean_pattern.regex.compiler import DefaultRegexCompiler

import pytest

def test_patternfinder_find(business):
    """test the patternfinder find method"""
    pf = PatternFinder(
        tokenizer='default',
        aligner='group',
        compiler=DefaultRegexCompiler()
    )

    patterns = pf.find(series=business['Address '])
    assert len(patterns) == 4

    types = ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']
    for elements, type in zip(patterns[9].container, types):
        assert elements.element_type == type

    # test column wise pattern creator
    pf = PatternFinder(
        tokenizer='default',
        aligner='group',
        compiler=DefaultRegexCompiler(method='col')
    )

    patterns = pf.find(series=business['Address '])
    assert len(patterns) == 4

    types = ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']
    for elements, type in zip(patterns[9].container, types):
        assert elements.element_type == type