# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for the PatternFinder Class"""

from openclean_pattern.patternfinder import PatternFinder

import pytest

def test_patternfinder_find(business):
    pf = PatternFinder(
        series=business['Address '],
        tokenizer='default',
        aligner='group'
    )

    patterns = pf.find()
    assert len(patterns)==3
    assert patterns[9] == ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']
    assert patterns[5] == ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']
    assert patterns[7] == ['DIGIT', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA', 'SPACE_REP', 'ALPHA']