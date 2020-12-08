# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for patterns class"""


from openclean_pattern.regex.compiler import DefaultRegexCompiler
from openclean_pattern.regex.base import SingularRowPattern, PatternElement
from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.tokenize.regex import DefaultTokenizer
from openclean_pattern.align.group import Group

ROWS = [['32A West Broadway 10007'],
        ['54E East Village 10003']]

def test_patterns_object(business):
    compiler = DefaultRegexCompiler()
    tokenizer = DefaultTokenizer()
    collector = Group()

    tokenized = tokenizer.encode(business['Address '])
    alignments = collector.collect(tokenized)

    patterns = compiler.compile(tokenized, alignments)

    assert len(patterns[7]) == 1
    for k, pat in patterns[7].items():
        assert pat.idx == {1,4,6,7,10,11,13,15}


    anomalies = compiler.mismatches(tokenized, patterns[7].top(pattern=True))
    assert list(business.loc[anomalies,'Address '].index) == [0, 2, 3, 5, 8, 9, 12, 14, 16, 17, 18, 19]


def test_patterns_insert():
    tokenizer = DefaultTokenizer()
    tokenized = tokenizer.encode(ROWS)

    pattern = SingularRowPattern()
    [pattern.container.append(PatternElement(r)) for r in tokenized[0]]

    assert pattern[0].element_type == SupportedDataTypes.ALPHANUM.name \
        and pattern[0].partial_regex == '32a'
    assert pattern[1].element_type == SupportedDataTypes.SPACE_REP.name \
        and pattern[1].partial_regex == ' '
    assert pattern[2].element_type == SupportedDataTypes.ALPHA.name \
        and pattern[2].partial_regex == 'west'
    assert pattern[3].element_type == SupportedDataTypes.SPACE_REP.name \
        and pattern[3].partial_regex == ' '
    assert pattern[4].element_type == SupportedDataTypes.ALPHA.name \
        and pattern[4].partial_regex == 'broadway'
    assert pattern[5].element_type == SupportedDataTypes.SPACE_REP.name \
        and pattern[5].partial_regex == ' '
    assert pattern[6].element_type == SupportedDataTypes.DIGIT.name \
        and pattern[6].partial_regex == '10007'


def test_patterns_update():
    tokenizer = DefaultTokenizer()
    tokenized = tokenizer.encode(ROWS)
    pattern = SingularRowPattern()

    for row in tokenized:
        if len(pattern) == 0:
            for r in row:
                pattern.container.append(PatternElement(r))
        else:
            pattern.update(row)

    assert pattern[0].element_type == SupportedDataTypes.ALPHANUM.name \
                   and pattern[0].partial_regex == 'XXX'
    assert pattern[1].element_type == SupportedDataTypes.SPACE_REP.name \
                   and pattern[1].partial_regex == ' '
    assert pattern[2].element_type == SupportedDataTypes.ALPHA.name \
                   and pattern[2].partial_regex == 'XXst'
    assert pattern[3].element_type == SupportedDataTypes.SPACE_REP.name \
                   and pattern[3].partial_regex == ' '
    assert pattern[4].element_type == SupportedDataTypes.ALPHA.name \
                   and pattern[4].partial_regex == 'XXXXXXXX'
    assert pattern[5].element_type == SupportedDataTypes.SPACE_REP.name \
                   and pattern[5].partial_regex == ' '
    assert pattern[6].element_type == SupportedDataTypes.DIGIT.name \
                   and pattern[6].partial_regex == '1000X'


