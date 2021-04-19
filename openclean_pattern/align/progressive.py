# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""implements the progressive aligner"""

from openclean_pattern.align.base import Aligner, Sequence, Alignment
from openclean_pattern.datatypes.base import SupportedDataTypes, create_gap_token
from openclean_pattern.datatypes.resolver import TypeResolver
from openclean_pattern.collect.neighbor import NeighborJoin
from openclean_pattern.align.distance.tree_edit import TreeEditDistance
from openclean_pattern.align.needlemanwunsch import NeedlemanWunschAligner
from openclean_pattern.utils.utils import list_contains_list

from collections import defaultdict, deque
from itertools import product
from typing import List, Dict, Union

ALIGN_PRO = "pro"
GAP = SupportedDataTypes.GAP


class ProgressiveAligner(Aligner):
    """
    Implementation of ClustalW using Progressive Alignment from https://math.mit.edu/classes/18.417/Slides/alignment.pdf

    The steps to achieve a ClustalW progessive multiple sequence alignment for a column are as follows:
        Compute all pairwise Needleman-Wunsch alignments (https://www.cs.sjsu.edu/~aid/cs152/NeedlemanWunsch.pdf and https://upload.wikimedia.org/wikipedia/en/c/c4/ParallelNeedlemanAlgorithm.pdf).
        Compute all against all pairwise edit distances and cluster to create a 'guide tree'.
        Align the closest 2.
        Repeat 1 to 3 for next closest until we get a final alignment.

    Can clustering in Key Collision be thought of as Candidate Alignment filter like in Facet: http://facet.cs.arizona.edu/parameter_advising.html

    # todo: Future work ideas:
        Identify the best multiple sequence alignment from all possibilities after step 4 using core column prediction techniques. Ref: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5397798/
        Create Profiles of various positions
    """

    def __init__(self, pairwise: Aligner = None, gap_penalty: float = 1, use_guide_tree: bool = True):
        """initializes the Progressive Aligner

        Parameters
        ----------
        pairwise: Aligner
            accepts an aligner to perform pairwise alignment of 2 input sequences
        gap_penalty: bool
            controls the penalty term for introducing gaps
        use_guide_tree: bool
            flag to use Neearest Neighbor Joining clustering to compute sequence of the iteration
        """
        super(ProgressiveAligner, self).__init__(ALIGN_PRO)
        self.pairwise = NeedlemanWunschAligner() if pairwise is None else pairwise
        self.dist = lambda x, y: 0 if TreeEditDistance(strict=False).compute([x], [
            y]) == 0 else 2 if x.regex_type is GAP or y.regex_type is GAP else 3

        self.min_samples = 4
        self.eps = .5

        self.gap_penalty = gap_penalty
        self.use_guide_tree = use_guide_tree

    def _get_pairs(self, aln: List) -> Dict:
        """input list of alignments / sequences. e.g. ['w- 123 st----','w. 12- street']
        and get pairs e.g.[['w','w'],['-','.']...]

        Parameters
        ----------
        aln: list
            input list to get pairs of

        Returns
        -------
            dict of lists containing piecewise pairs for each position
        """
        R = len(aln) if isinstance(aln, Alignment) else 1
        C = len(aln[0]) if isinstance(aln, Alignment) else len(aln)

        pairs = defaultdict(list)
        [pairs[-1].append(create_gap_token(i)) for i in range(R)]

        for j in range(C):
            if isinstance(aln, Alignment):
                for seq in aln:
                    pairs[j].append(seq[j])
            elif isinstance(aln, Sequence):
                pairs[j].append(aln[j])
            else:
                raise ValueError("Expected Alignment or Sequence")

        return pairs

    def _pairwise_dist(self, pair1: List, pair2: List) -> float:
        """calculates the total pair distance

        pair1 could be: ['W','S'] and pair 2 ['-','N']
        The distance would be the sum of the dot product: d('W','-') + d('W','N') + d('S','-') + d('S','N')

        Parameters
        ----------
        pair1: list
            distance source component
        pair2: list
            distance destination component

        Returns
        -------
            float distance
        """
        distance = 0
        for x in pair1:
            for y in pair2:
                distance += self.dist(x, y)

        return distance

    def _init_matrix(self, aln: List, seq: List) -> Dict:
        """takes the alignment and the sequences/alignments and returns the initialized F marix containing
        the pairwise similarities as starting indices

        e.g.
            aln = ['W. 123 St----','W- 12- Street'] , seq = ['12 W St']

             |   | -  | W | . |    | 1  | 2  | 3  |    | S  | t  | -  | -  | -  | -  |
             |   | -  | W | - |    | 1  | 2  | -  |    | S  | t  | r  | e  | e  | t  |
             | - | 0  | 4 | 6 | 10 | 14 | 18 | 20 | 24 | 28 | 32 | 34 | 36 | 38 | 40 |
             | 1 | 4  |
             | 2 | 8  |
             |   | 12 |
             | W | 16 |
             |   | 20 |
             | S | 24 |
             | t | 28 |

        Parameters
        ----------
        aln: Alignment
            the rows of the pairwise init matrix
        seq: Sequence
            the columns of the pairwise init matrix

        Returns
        -------
            an initialization matrix as a dictionary
        """
        F = dict()

        for ci in aln:
            pre = 0 if ci == -1 else F[-1, ci - 1]
            F[-1, ci] = (pre + self._pairwise_dist(aln[ci], seq[-1]))

        for ri in seq:
            pre = 0 if ri == -1 else F[ri - 1, -1]
            F[ri, -1] = (pre + self._pairwise_dist(seq[ri], aln[-1]))

        return F

    def _align_order(self, order: List) -> Alignment:
        """align lists of input sequences with ordering information as follows:
            ['AA',('DC,'FC')] -- merges ('DC'+'FC')+'AA'

            more explicitly:
            [R1,(R2, R3)] where R1=('alpha','num'), R2=('alphanum','num'), R3=('alpha','punc') merges (R2 + R3) + R1

        Parameters
        ----------
        order: list
            the list of sequences and alignments to merge

        Returns
        -------
            an ordered list of the local alignment
        """

        if len(order) == 1:
            v = order[0]
            if isinstance(v, Sequence):
                return Alignment.from_sequences([v])
            elif isinstance(v, Alignment):
                return v
            else:
                raise ValueError("Invalid Input")

        computed_alignments = list()
        pair_sequences = list()
        free_sequences = list()

        for val in order:
            if isinstance(val, Sequence):
                free_sequences.append(val)
            elif isinstance(val, Alignment):
                computed_alignments.append(val)
            else:
                pair_sequences.append(val)

        # align all pairs
        for pair in pair_sequences:
            paln = Alignment(())
            for pseq in pair:
                if len(paln) == 0:
                    paln = Alignment.from_sequences([pseq])
                else:
                    paln = Alignment(self._align(paln, pseq))
            if len(paln):
                computed_alignments.append(paln)

        # align free sequences
        faln = Alignment(())
        for seq in free_sequences:
            if len(faln) == 0:
                faln = Alignment.from_sequences([seq])
            else:
                faln = Alignment(self._align(faln, seq))
        if len(faln):
            computed_alignments.append(faln)

        # align all alignments
        aln = computed_alignments[0]
        for al in computed_alignments[1:]:
            aln = Alignment(self._align(aln, al))

        return aln

    def align_guide_tree(self, guide: List) -> Alignment:
        """accepts a tupled guide tree and aligns it recursively starting from inner most node

        Parameters
        ----------
        guide: list
            The guide to recursively iterate over and create an overall alignment starting merging from the inner
            most node

        Returns
        -------
            an aligned column
        """

        def traverse(o, func):
            """traverses the order array finding the deepest node"""
            for item in o:
                if isinstance(item, str) or isinstance(item, tuple):
                    yield item
                elif isinstance(item, list):
                    if not list_contains_list(item):
                        a = func(item)
                        yield a
                    else:
                        yield list(traverse(item, func))

        def apply_func(order, func):
            """perform the func starting with the inner most list moving outwards till no inner list remains"""
            while list_contains_list(order):
                order = list(traverse(order, func))
            return func(order)

        return apply_func(guide, self._align_order)

    def align_column(self, column: List) -> Alignment:
        """aligns an input column without any extra inbuilt aligning information e.g. alignment order. For
        alignment with order, see self.align_guide_tree

        Parameters
        ----------
        column: list
            the list of Tokens to align

        Returns
        -------
            an aligned column
        """
        pair = tuple()
        if len(column) >= 2:
            pair = (Sequence.from_tokens(column[0]), Sequence.from_tokens(column[1]))
            if len(column) == 2:
                return self._align_order(pair)
            for i, c in enumerate(column):
                if i > 1:
                    pair = (pair, Sequence.from_tokens(c))
        elif len(column) == 1:
            pair = (Sequence.from_tokens(column[0]),)

        return self._align_order(pair)


    def _align(self, x: Union[Sequence, Alignment], y: Union[Sequence, Alignment]) -> Alignment:
        """adds a single sequence to the alignment

        Parameters
        ----------
        x: Alignment or Sequence
            the current local/global alignment
        y: Alignment or Sequence
            the sequence or alignment to add to it

        Returns
        -------
            an Alignment with the Sequence added
        """
        if not (isinstance(x, Alignment) or isinstance(x, Sequence)) or \
                not (isinstance(y, Sequence) or isinstance(y, Alignment)):
            raise ValueError("Invalid Input")

        # single sequence/sequence or sequence/alignment but not alignment/alignment
        if not (isinstance(x, Alignment) and isinstance(y, Alignment)) and len(x) == 1:
            return self.pairwise.align([x[0], y])

        DIAG = -1, -1
        LEFT = -1, 0
        UP = 0, -1

        # Create tables F and Ptr and get costing
        Ptr = {}

        aln = self._get_pairs(x)
        seq = self._get_pairs(y)

        N = len(aln) - 1
        M = len(seq) - 1

        F = self._init_matrix(aln, seq)

        option_Ptr = DIAG, LEFT, UP

        for i, j in product(range(M), range(N)):
            option_F = (
                F[i - 1, j - 1] + self._pairwise_dist(aln[j], seq[i]),
                F[i - 1, j] + self.gap_penalty,
                F[i, j - 1] + self.gap_penalty,
            )
            F[i, j], Ptr[i, j] = min(zip(option_F, option_Ptr))

        # Work backwards from (N - 1, M - 1) to (0, 0)
        # to find the best alignment.
        alignment = deque()
        j, i = N - 1, M - 1
        while i >= 0 and j >= 0:
            direction = Ptr[i, j]
            if direction == DIAG:
                element = i, j
            elif direction == LEFT:
                element = i, GAP
            elif direction == UP:
                element = GAP, j
            alignment.appendleft(element)
            di, dj = direction
            i, j = i + di, j + dj
        while i >= 0:
            alignment.appendleft((i, GAP))
            i -= 1
        while j >= 0:
            alignment.appendleft((GAP, j))
            j -= 1

        als = self._resolve_alignment(alignment, x, y)

        return als

    def _resolve_alignment(self, gap_info, x, y) -> Alignment:
        """inserts gaps into input sequences/alignments as per the latest computation and merges them into a full alignment

        Parameters
        ----------
        gap_info: list
            the latest computed alignment of x and y with gap placements
        x: Sequence/Alignment
            the first component in the alignment object
        y: Sequence/Alignment
            the second component in the alignment object

        Returns
        -------
            merged alignment with gaps of x and y
        """
        for n, a in enumerate(gap_info):
            j, i = a
            if i is GAP:
                x = x.insert_gap(n)

            if j is GAP:
                y = y.insert_gap(n)

        return Alignment.from_tuple((x, y))

    def align(self, column: List, groups: Dict) -> List[Alignment]:
        """Takes in the column and the groups and returns an aligned version of each group by adding Gap tokens to each row.
        A list[Tuple(Tokens)] is returned with the aligned values

        Parameters
        ----------
        column: list[Tuple(Tokens)]
            The column to align
        groups: dict
            The dict of groups with group id as key and row indices as values

        Returns
        -------
            dict[Alignment]
        """
        aligned = list()
        for cluster, idx in groups.items():
            #  pad the smaller ones with gap characters
            col = list()
            for id in idx:
                if not isinstance(id, int):
                    raise KeyError("row indices should be int. found: {}".format(id))
                col.append(column[id])

            if not self.use_guide_tree or len(col) < 3:
                aligned_cluster = self.align_column(col)
            else:
                nj = NeighborJoin()
                tree, grps = nj.get_tree_and_order(col)
                aligned_cluster = self.align_guide_tree(grps)

            aligned.append(aligned_cluster)

        return aligned
