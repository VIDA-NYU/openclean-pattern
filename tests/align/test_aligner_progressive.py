# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for Pad class"""


from openclean_pattern.align.progressive import ProgressiveAligner, NeedlemanWunschAligner
from openclean_pattern.tokenize.factory import DefaultTokenizer
from openclean_pattern.datatypes.base import SupportedDataTypes


def test_needleman_wunsch():
    """test the needlenman wunsch pairwise aligner"""
    x = 'W. 125 ST' # alpha punc space digit space alpha
    y = 'W125 ST' # alphanum space alpha

    column = [x, y]

    rows = DefaultTokenizer().encode(column)
    aligned = NeedlemanWunschAligner.align(rows[0], rows[1])

    assert len(aligned) == len(rows)
    assert len(aligned[1]) == len(aligned[0])

    # many alignments possible but last alpha and 1 space should always be aligned
    assert aligned[0][-1].regex_type == aligned[1][-1].regex_type == SupportedDataTypes.ALPHA
    assert aligned[0][2].regex_type == aligned[1][2].regex_type == SupportedDataTypes.SPACE_REP or \
           aligned[0][4].regex_type == aligned[1][4].regex_type == SupportedDataTypes.SPACE_REP

    z = '12BROADWAY.AVE'
    rows = DefaultTokenizer().encode([y, z])
    aligned = NeedlemanWunschAligner.align(rows[0], rows[1])

    assert len(aligned) == len(rows)
    assert len(aligned[1]) == len(aligned[0])

    assert aligned[0][0].regex_type == aligned[1][0].regex_type == SupportedDataTypes.ALPHANUM
    assert aligned[0][1].regex_type == SupportedDataTypes.SPACE_REP and aligned[1][1].regex_type == SupportedDataTypes.PUNCTUATION
    assert aligned[0][-1].regex_type == aligned[1][-1].regex_type == SupportedDataTypes.ALPHA
