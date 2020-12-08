# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for the OpencleanPatternFinder Class"""

from openclean_pattern.opencleanpatternfinder import OpencleanPatternFinder
from openclean_pattern.regex.compiler import DefaultRegexCompiler

import pytest

def test_patternfinder_find(business):
    """test the patternfinder find method"""
    pf = OpencleanPatternFinder(
        tokenizer='default',
        aligner='pad',
        compiler=DefaultRegexCompiler()
    )

    patterns = pf.find(series=business['Address '])
    assert len(patterns) == 4

    types = ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']
    assert len(patterns[9]) == 1
    for k, pat in patterns[9].items():
        for elements, type in zip(pat.container, types):
            assert elements.element_type == type

    # test column wise pattern creator
    pf = OpencleanPatternFinder(
        tokenizer='default',
        aligner='pad',
        compiler=DefaultRegexCompiler(method='col')
    )

    patterns = pf.find(series=business['Address '])
    assert len(patterns) == 4

    types = ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']
    assert len(patterns[9]) == 1
    for k, pat in patterns[9].items():
        for elements, type in zip(pat.container, types):
            assert elements.element_type == type