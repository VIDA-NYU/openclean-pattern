# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for the OpencleanPatternFinder Class"""

from openclean_pattern.datatypes.base import SupportedDataTypes as DT
from openclean_pattern.opencleanpatternfinder import OpencleanPatternFinder
from openclean_pattern.regex.compiler import DefaultRegexCompiler


def test_patternfinder_find(business):
    """test the patternfinder find method"""
    pf = OpencleanPatternFinder(
        tokenizer='default',
        aligner='pad',
        compiler=DefaultRegexCompiler()
    )

    patterns = pf.find(series=business['Address '])
    assert len(patterns) == 4

    types = [DT.DIGIT, DT.SPACE_REP, DT.ALPHA, DT.SPACE_REP, DT.ALPHA, DT.SPACE_REP, DT.ALPHA, DT.SPACE_REP, DT.ALPHA]
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

    types = [DT.DIGIT, DT.SPACE_REP, DT.ALPHA, DT.SPACE_REP, DT.ALPHA, DT.SPACE_REP, DT.ALPHA, DT.SPACE_REP, DT.ALPHA]
    assert len(patterns[9]) == 1
    for k, pat in patterns[9].items():
        for elements, type in zip(pat.container, types):
            assert elements.element_type == type
