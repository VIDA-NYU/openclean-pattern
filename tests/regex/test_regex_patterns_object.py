# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for patterns class"""


from openclean_pattern.regex.base import RowWiseCompiler
from openclean_pattern.tokenize.regex import DefaultTokenizer
from openclean_pattern.align.group import GroupAligner

def test_patterns_object(business):
    compiler = RowWiseCompiler()
    tokenizer = DefaultTokenizer()
    aligner = GroupAligner()

    tokenized = tokenizer.encode(business['Address '])
    alignments = aligner.align(tokenized)

    patterns = compiler.compile(tokenized, alignments)

    assert patterns[7].idx == {1,4,6,7,10,11,13,15}

    anomalies = compiler.anomalies(tokenized, alignments)
    assert anomalies[7] == [0,8,3,12,14]

