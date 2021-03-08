# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""unit tests for patterns class"""


from openclean_pattern.regex.compiler import DefaultRegexCompiler
from openclean_pattern.regex.base import SingularRowPattern, PatternElement, PatternElementSizeMonitor
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


def test_pattern_element_set(business, year):
    tokenizer = DefaultTokenizer()
    tokenized = tokenizer.encode(business['Address '])
    tokenized = [tokenized[0][4], tokenized[0][6], tokenized[1][2], tokenized[1][4], tokenized[1][6]] # mixing matching a bunch of ALPHAs
    for i, t in enumerate(tokenized): # updating row idx for the synthetic data
        t.rowidx = i

    pet = PatternElementSizeMonitor()
    for t in tokenized:
        pet.update(t)

    pe = pet.load()

    assert isinstance(pe, PatternElement)
    assert pe.idx == set([0,1,2,3,4])
    assert pe.element_type == 'ALPHA'
    assert pe.len_max == 5
    assert pe.len_min == 1
    assert len(pe.values) > 0
    for i in pe.values:
        assert i in ['st','ne','w','ave','davis']

    tokenized = tokenizer.encode(year)
    months = [t[0] for t in tokenized]
    pet = PatternElementSizeMonitor()
    for t in months:
        pet.update(t)

    pe = pet.load()
    assert isinstance(pe, PatternElement)
    assert pe.element_type == 'ALPHA'
    assert len(pe.values) > 0
    for i in pe.values: #verify values are accessible
        assert i in ['july','april']


def test_pattern_without_anomalous_elements(checkintime, specimen):
    """Test if anomalous values (<90% of the dataset) are excluded during pattern element generation

    Process for creating PatternElements:
     1. create sets of differently lengthed values (e.g. 2 sets total, 1 for ['ne','st'] and 1 for ['w']
     2. start combining sets together in descending order of their frequencies (so largest sets down to the smallest ones)
     3. stop when you've added 90% of the data
     4. sets smaller than this are excluded

     Example: (assuming @ 20% threshold for 5 values)
         For a Pattern Element ALPHA with values: 'ave','str','nes','jtd','st'

        1. Create sets:
            A: Size 3, Freq 4: [ave, str, nes, jtd]
            B: Size 2, Freq 1: [st]

        2-4. Update Pattern Element
            create new PatternElement()
            add set A to it
            check freq/total = 0.8 == threshold
            dont add set B

        The final Patten element ~ ALPHA (3-3) instead of ALPHA(2-3)
    """
    # The dataset contains 9 anomalous values for the 5th position (year) thus the pattern element = DIGIT[4-5] instead of DIGIT[4-4]
    # without anomaly removal = ['DIGIT[2-2]', '/', 'DIGIT[2-2]', '/', 'DIGIT[4-5]', 'SPACE_REP[1-1]', 'DIGIT[2-2]', ':', 'DIGIT[2-2]', ':',
    #  'DIGIT[2-2]', 'SPACE_REP[1-1]', 'ALPHA[2-2]', 'SPACE_REP[1-1]', '+', 'DIGIT[4-4]']

    checkin_truth = ['DIGIT[2-2]', '/', 'DIGIT[2-2]', '/', 'DIGIT[4-4]', 'SPACE_REP[1-1]', 'DIGIT[2-2]', ':', 'DIGIT[2-2]', ':',
     'DIGIT[2-2]', 'SPACE_REP[1-1]', 'ALPHA[2-2]', 'SPACE_REP[1-1]', '+', 'DIGIT[4-4]']

    specimen_truth = ['DIGIT[4-4]', '/', 'DIGIT[2-2]', '/', 'DIGIT[2-2]']

    compiler1 = DefaultRegexCompiler(method='col')
    compiler2 = DefaultRegexCompiler(method='row')

    def test(df, compiler, truth):
        collector = Group()
        tokenizer = DefaultTokenizer()

        # Get a sample of terms from the column.
        terms = list(df)

        # Tokenize and convert tokens into representation.
        tokenized_terms = tokenizer.encode(terms)

        # Group tokenized terms by number of tokens.
        clusters = collector.collect(tokenized_terms)

        for _, term_ids in clusters.items():
            if len(term_ids) / len(terms) < 0.9:
                # Ignore small clusters.
                continue

            # Return the pattern for the found cluster. This assumes that
            # maximally one cluster can satisfy the threshold.
            patterns = compiler.compile(tokenized_terms, {0: term_ids})[0]
            break

        if patterns:
            tokens = list()
            for el in patterns.top(n=1, pattern=True):
                if el.punc_list:
                    token = ''.join(el.punc_list)
                else:
                    token = '{}[{}-{}]'.format(el.element_type, el.len_min, el.len_max)
                tokens.append(token)

        for actual, expected in zip(tokens, truth):
            assert actual == expected

    for df, truth in [(checkintime, checkin_truth), (specimen, specimen_truth)]:
        for compiler in [compiler1, compiler2]:
            test(df, compiler, truth)


def test_anomalous_values_in_mismatches(checkintime):
    """Test if values not included in the pattern elements are identified as mismatches
    """
    collector = Group()
    tokenizer = DefaultTokenizer()
    compiler = DefaultRegexCompiler(method='col')

    # Get a sample of terms from the column.
    terms = list(checkintime)

    # Tokenize and convert tokens into representation.
    tokenized_terms = tokenizer.encode(terms)

    # Group tokenized terms by number of tokens.
    clusters = collector.collect(tokenized_terms)

    for _, term_ids in clusters.items():
        if len(term_ids) / len(terms) < 0.9:
            # Ignore small clusters.
            continue

        # Return the pattern for the found cluster. This assumes that
        # maximally one cluster can satisfy the threshold.
        patterns = compiler.compile(tokenized_terms, {0: term_ids})[0]
        break

    pattern = patterns.top(n=1, pattern=True)

    mismatches = list()
    for term in terms:
        if not pattern.compare(term, tokenizer):
            mismatches.append(term)

    assert mismatches == ['04/22/43971 02:40:00 AM +0000', '01/11/43972 04:40:00 PM +0000', '10/03/43971 04:40:00 PM +0000',
     '04/20/43971 12:40:00 AM +0000', '05/08/43971 06:40:00 PM +0000', '08/29/43971 06:40:00 AM +0000',
     '08/27/43971 04:40:00 AM +0000', '10/03/43971 12:00:00 AM +0000', '10/16/43971 09:20:00 PM +0000']