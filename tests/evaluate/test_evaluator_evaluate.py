# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for Evaluator class"""

from openclean_pattern.opencleanpatternfinder import OpencleanPatternFinder
from openclean_pattern.regex.compiler import DefaultRegexCompiler


def test_evaluator_evaluate(business):
    """Creates a pattern and evaluates it on the same column to see if mismatches are the same as mismatches
    """
    pf = OpencleanPatternFinder(
        tokenizer='default',
        collector='group',
        compiler=DefaultRegexCompiler()
    )

    patterns = pf.find(series=business['Address '])
    eval_pattern = patterns[7].top(pattern=True)

    predicate = pf.compare(eval_pattern, business['Address '].tolist(), negate=True)
    mismatches = business.loc[predicate, 'Address ']
    mismatched_pattern = pf.find(mismatches)

    for mp in mismatched_pattern.values():
        assert not mp == eval_pattern

    predicate = pf.compare(eval_pattern, business['Address '].tolist(), negate=False)
    matches = business.loc[predicate, 'Address ']
    matched_pattern = pf.find(matches)

    assert len(matched_pattern) == 1
    assert matched_pattern[7].top(pattern=True) == eval_pattern