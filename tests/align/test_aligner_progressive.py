# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for Progressive alignment class"""

from openclean_pattern.align.progressive import ProgressiveAligner
from openclean_pattern.tokenize.factory import DefaultTokenizer, RegexTokenizer
from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import DefaultTypeResolver, DateResolver
from openclean_pattern.align.base import Alignment

ADDRESSES = ['123 ST', '21W.AVENUE', 'WEST ALLEN 12']


def test_progressive_align():
    dt = DefaultTokenizer()
    encoded = dt.encode(ADDRESSES)

    pa = ProgressiveAligner()
    aln = pa.align(encoded, {0: [0, 1, 2]})[0]

    assert len(aln) == 3
    assert aln[0][0].regex_type == SupportedDataTypes.ALPHANUM
    assert aln[0][1].regex_type == SupportedDataTypes.PUNCTUATION
    assert aln[0][2].regex_type == SupportedDataTypes.ALPHA
    assert aln[0][3].regex_type == SupportedDataTypes.GAP
    assert aln[0][4].regex_type == SupportedDataTypes.GAP

    assert aln[1][0].regex_type == SupportedDataTypes.DIGIT
    assert aln[1][1].regex_type == SupportedDataTypes.SPACE_REP
    assert aln[1][2].regex_type == SupportedDataTypes.ALPHA
    assert aln[1][3].regex_type == SupportedDataTypes.GAP
    assert aln[1][4].regex_type == SupportedDataTypes.GAP

    assert aln[2][0].regex_type == SupportedDataTypes.ALPHA
    assert aln[2][1].regex_type == SupportedDataTypes.SPACE_REP
    assert aln[2][2].regex_type == SupportedDataTypes.ALPHA
    assert aln[2][3].regex_type == SupportedDataTypes.SPACE_REP
    assert aln[2][4].regex_type == SupportedDataTypes.DIGIT


def test_progressive_align_wo_tree():
    dt = DefaultTokenizer()
    encoded = dt.encode(ADDRESSES)

    pa = ProgressiveAligner(use_guide_tree=False)
    aln = pa.align(encoded, {0: [0, 1, 2]})[0]

    assert len(aln) == 3
    assert aln[0][0].regex_type == SupportedDataTypes.DIGIT
    assert aln[0][1].regex_type == SupportedDataTypes.SPACE_REP
    assert aln[0][2].regex_type == SupportedDataTypes.ALPHA
    assert aln[0][3].regex_type == SupportedDataTypes.GAP
    assert aln[0][4].regex_type == SupportedDataTypes.GAP

    assert aln[1][0].regex_type == SupportedDataTypes.ALPHANUM
    assert aln[1][1].regex_type == SupportedDataTypes.PUNCTUATION
    assert aln[1][2].regex_type == SupportedDataTypes.ALPHA
    assert aln[1][3].regex_type == SupportedDataTypes.GAP
    assert aln[1][4].regex_type == SupportedDataTypes.GAP

    assert aln[2][0].regex_type == SupportedDataTypes.ALPHA
    assert aln[2][1].regex_type == SupportedDataTypes.SPACE_REP
    assert aln[2][2].regex_type == SupportedDataTypes.ALPHA
    assert aln[2][3].regex_type == SupportedDataTypes.SPACE_REP
    assert aln[2][4].regex_type == SupportedDataTypes.DIGIT


def test_progressive_align_dates(dates):
    dt = DefaultTokenizer()

    encoded = dt.encode(dates)

    pa = ProgressiveAligner(use_guide_tree=False)
    aln = pa.align(encoded, {0: [0, 1, 2], 1: [3]})

    for al in aln:
        assert isinstance(al, Alignment)

    al = aln[0]
    assert len(al) == 3
    assert al[0][0].regex_type == SupportedDataTypes.ALPHA
    assert al[0][1].regex_type == SupportedDataTypes.PUNCTUATION
    assert al[0][2].regex_type == SupportedDataTypes.SPACE_REP
    assert al[0][3].regex_type == SupportedDataTypes.ALPHANUM
    assert al[0][4].regex_type == SupportedDataTypes.SPACE_REP
    assert al[0][5].regex_type == SupportedDataTypes.ALPHA
    assert al[0][6].regex_type == SupportedDataTypes.PUNCTUATION
    assert al[0][7].regex_type == SupportedDataTypes.SPACE_REP
    assert al[0][8].regex_type == SupportedDataTypes.DIGIT

    assert al[1][0].regex_type == SupportedDataTypes.ALPHA
    assert al[1][1].regex_type == SupportedDataTypes.PUNCTUATION
    assert al[1][2].regex_type == SupportedDataTypes.SPACE_REP
    assert al[1][3].regex_type == SupportedDataTypes.ALPHA
    assert al[1][4].regex_type == SupportedDataTypes.SPACE_REP
    assert al[1][5].regex_type == SupportedDataTypes.DIGIT
    assert al[1][6].regex_type == SupportedDataTypes.PUNCTUATION
    assert al[1][7].regex_type == SupportedDataTypes.SPACE_REP
    assert al[1][8].regex_type == SupportedDataTypes.DIGIT

    assert al[2][0].regex_type == SupportedDataTypes.ALPHA
    assert al[2][1].regex_type == SupportedDataTypes.GAP
    assert al[2][2].regex_type == SupportedDataTypes.SPACE_REP
    assert al[2][3].regex_type == SupportedDataTypes.ALPHA
    assert al[2][4].regex_type == SupportedDataTypes.GAP
    assert al[2][5].regex_type == SupportedDataTypes.GAP
    assert al[2][6].regex_type == SupportedDataTypes.GAP
    assert al[2][7].regex_type == SupportedDataTypes.SPACE_REP
    assert al[2][8].regex_type == SupportedDataTypes.DIGIT

    al = aln[1]
    assert len(al) == 1
    assert al[0][0].regex_type == SupportedDataTypes.ALPHA
    assert al[0][1].regex_type == SupportedDataTypes.SPACE_REP
    assert al[0][2].regex_type == SupportedDataTypes.DIGIT


def test_progressive_align_dates_nonbasic(dates):
    dtr = DefaultTypeResolver(interceptors=[DateResolver()])
    rt = RegexTokenizer(type_resolver=dtr)

    encoded = rt.encode(dates)

    pa = ProgressiveAligner(use_guide_tree=False)
    aln = pa.align(encoded, {0: [0, 1, 2], 1: [3]})

    for al in aln:
        assert isinstance(al, Alignment)

    al = aln[0]
    assert len(al) == 3
    assert al[0][0].regex_type == SupportedDataTypes.WEEKDAY
    assert al[0][1].regex_type == SupportedDataTypes.PUNCTUATION
    assert al[0][2].regex_type == SupportedDataTypes.SPACE_REP
    assert al[0][3].regex_type == SupportedDataTypes.ALPHANUM
    assert al[0][4].regex_type == SupportedDataTypes.SPACE_REP
    assert al[0][5].regex_type == SupportedDataTypes.MONTH
    assert al[0][6].regex_type == SupportedDataTypes.PUNCTUATION
    assert al[0][7].regex_type == SupportedDataTypes.GAP
    assert al[0][8].regex_type == SupportedDataTypes.SPACE_REP
    assert al[0][9].regex_type == SupportedDataTypes.DIGIT

    assert al[1][0].regex_type == SupportedDataTypes.WEEKDAY
    assert al[1][1].regex_type == SupportedDataTypes.PUNCTUATION
    assert al[1][2].regex_type == SupportedDataTypes.SPACE_REP
    assert al[1][3].regex_type == SupportedDataTypes.MONTH
    assert al[1][4].regex_type == SupportedDataTypes.SPACE_REP
    assert al[1][5].regex_type == SupportedDataTypes.DIGIT
    assert al[1][6].regex_type == SupportedDataTypes.PUNCTUATION
    assert al[1][7].regex_type == SupportedDataTypes.GAP
    assert al[1][8].regex_type == SupportedDataTypes.SPACE_REP
    assert al[1][9].regex_type == SupportedDataTypes.DIGIT

    assert al[2][0].regex_type == SupportedDataTypes.WEEKDAY
    assert al[2][1].regex_type == SupportedDataTypes.GAP
    assert al[2][2].regex_type == SupportedDataTypes.GAP
    assert al[2][3].regex_type == SupportedDataTypes.GAP
    assert al[2][4].regex_type == SupportedDataTypes.GAP
    assert al[2][5].regex_type == SupportedDataTypes.GAP
    assert al[2][6].regex_type == SupportedDataTypes.SPACE_REP
    assert al[2][7].regex_type == SupportedDataTypes.MONTH
    assert al[2][8].regex_type == SupportedDataTypes.SPACE_REP
    assert al[2][9].regex_type == SupportedDataTypes.DIGIT

    al = aln[1]
    assert len(al) == 1
    assert al[0][0].regex_type == SupportedDataTypes.MONTH
    assert al[0][1].regex_type == SupportedDataTypes.SPACE_REP
    assert al[0][2].regex_type == SupportedDataTypes.DIGIT
