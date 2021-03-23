# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""implements the progressive aligner"""


from openclean_pattern.align.base import Aligner
from openclean_pattern.datatypes.base import SupportedDataTypes

from collections import defaultdict, deque
from itertools import product


ALIGN_PRO = "pro"
GAP = SupportedDataTypes.GAP


class NeedlemanWunschAligner:
    """
    Dynamic programming solution to the otherwise brute force sequence alignment problem vastly used for protien and nucleotide sequencing.
    Globally aligns two sequences at a time. Gap penalty and different initializations added here to allow different configurations.

    References
        https://www.cs.sjsu.edu/~aid/cs152/NeedlemanWunsch.pdf
        https://upload.wikimedia.org/wikipedia/en/c/c4/ParallelNeedlemanAlgorithm.pdf
    """

    @staticmethod
    def _align(x, y, keep_gaps_together):
        """aligns two inputs

        Parameters
        ----------
        x: str
            value 1
        y: str
            value 2
        keep_gaps_together: bool
            flag to allow different configurations

        Returns
        -------
            aligned list of lists
        """

        DIAG = -1, -1
        LEFT = -1, 0
        UP = 0, -1

        # Create tables F and Ptr and get costing
        F = dict()
        Ptr = {}

        F[-1, -1] = 0
        N, M = len(x), len(y)

        # 2i keeps gaps together, -i/-j injects gaps inside strings
        for i in range(N):
            F[i, -1] = -i if not keep_gaps_together else 2 * i
        for j in range(M):
            F[-1, j] = -j if not keep_gaps_together else 2 * j

        # heuristic optimal costing for sequences
        _eval = (lambda a, b: int(a.regex_type == b.regex_type)) if not keep_gaps_together else (lambda a, b: 2 if a.regex_type == b.regex_type else -3)

        option_Ptr = DIAG, LEFT, UP
        for i, j in product(range(N), range(M)):
            # no gap penatlies involved (or gap affines like in Gotoh's algorithm)
            option_F = (
                F[i - 1, j - 1] + _eval(x[i], y[j]),
                F[i - 1, j] - 1,
                F[i, j - 1] - 1,
            )
            F[i, j], Ptr[i, j] = max(zip(option_F, option_Ptr))

        # Work backwards from (N - 1, M - 1) to (0, 0)
        # to find the best alignment.
        alignment = deque()
        i, j = N - 1, M - 1
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

        return list(alignment), F

    @staticmethod
    def align(x, y, keep_gaps_together=False):
        alignment, _ = NeedlemanWunschAligner._align(x, y, keep_gaps_together)

        a, b = list(), list()
        for i, _ in alignment:
            if i is GAP:
                a.append(GAP)
            else:
                a.append(x[i])

        for _, j in alignment:
            if j is GAP:
                b.append(GAP)
            else:
                b.append(y[j])

        return a, b


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
    def __init__(self, pairwise=None, keep_gaps_together=False, gap_penalty=1, use_guide_tree=True):
        """initializes the Progressive Aligner
        """
        super(ProgressiveAligner, self).__init__(ALIGN_PRO)
        self.pairwise = NeedlemanWunschAligner() if pairwise is None else pairwise
        self.keep_gaps_together = keep_gaps_together

        self.dist = lambda x, y: 0 if x == y else 2 if x is GAP or y is GAP else 3

        self.min_samples = 4
        self.eps = .5

        self.gap_penalty = gap_penalty
        self.use_guide_tree = use_guide_tree

    def nj_cluster(self, column):
        from openclean.profiling.pattern.align.NJ_Cluster import get_tree_and_order

        tree, groups  = get_tree_and_order(column)

        return groups

    def cluster_and_align(self, column):
        """
        takes in a list of values
            - pairwise distances + cluster => guide tree
            - align each cluster
            - inter-cluster alignment?

        give matrices to align

            e.g.
            column_matrix = 2 x 4
            row_matrix = 4 x 2

            *pad extra Gaps

             |   | - | S | A | N | D |
             |   | - | - | A | N | D |
          -  | - |   |   |   |   |   |
          F  | B |   |   |   |   |   |
          E  | A |   |   |   |   |   |
          N  | N |   |   |   |   |   |
          D  | D |   |   |   |   |   |
        """
        aln1, order = self.nj_cluster(column)

        alignments = dict()
        header = None
        for al in aln1:
            if al != -1:
                if len(aln1[al]) > 1:
                    clstr = [column[i] for i in aln1[al]]
                    header, F = self.align_column(clstr)
                else:
                    header = aln1[al]
            alignments[al] = header

        return alignments

    def get_pairs(self, aln):
        """input list of alignments / sequences. e.g. ['w- 123 st----','w. 12- street']
        and get pairs e.g.[['w','w'],['-','.']...]
        """
        if isinstance(aln, str):
            aln = [aln]

        if not isinstance(aln, list) and not isinstance(aln, tuple):
            raise ValueError("expected a list or a tuple")

        N = len(aln[0])
        M = len(aln)

        pairs = defaultdict(list)

        [pairs[-1].append(GAP) for i in range(M)]

        for i, al in enumerate(aln):
            for j in range(N):
                pairs[j].append(al[j])

        return pairs

    def pairwise_dist(self, pair1, pair2):
        """calculates the total pair distance

        pair1 could be: ['W','S'] and pair 2 ['-','N']
        The distance would be the sum of the dot product: d('W','-') + d('W','N') + d('S','-') + d('S','N')
        """
        d = self.dist

        distance = 0
        for x in pair1:
            for y in pair2:
                distance += d(x, y)

        return distance

    def resolve_alignment(self, y, alignment, left=False):
        """
        converts the alignment matrix into human readable strings.
        If left is False, it is going to use the right value of each tuple in the alignment matrix
        """
        if left:
            yi = "".join(GAP if i is GAP else y[i] for i, _ in alignment)
        else:
            yi = "".join(GAP if i is GAP else y[i] for _, i in alignment)

        return yi

    def init_matrix(self, aln, seq):
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

        """
        F = dict()

        for ci in aln:
            pre = 0 if ci == -1 else F[-1, ci - 1]
            F[-1, ci] = (pre + self.pairwise_dist(aln[ci], seq[-1]))

        for ri in seq:
            pre = 0 if ri == -1 else F[ri - 1, -1]
            F[ri, -1] = (pre + self.pairwise_dist(seq[ri], aln[-1]))

        return F

    def align_column(self, column):
        """align lists of sequences and alignments
        ['asd', ('ads,'dds'),'wsa']
        """
        F = dict()
        computed_alignments = list()
        raw_values = list()
        for val in column:
            if isinstance(val, tuple):
                computed_alignments.append(val)
            else:
                raw_values.append(val)

        # align the values
        this_alignment = tuple()
        for value in raw_values:
            if len(this_alignment) == 0:
                this_alignment = (value,)
            else:
                this_alignment, F = self.align(this_alignment, value)

        # align all the alignments
        if len(computed_alignments) > 0 and len(this_alignment) > 0:
            for als in computed_alignments:
                this_alignment, F = self.align(this_alignment, als)

        elif len(computed_alignments) > 1 and len(this_alignment) == 0:
            this_alignment = computed_alignments[0]
            for als in computed_alignments[1:]:
                this_alignment, F = self.align(this_alignment, als)

        elif len(computed_alignments) == 1 and len(this_alignment) == 0:
            this_alignment = computed_alignments[0]

        return this_alignment, F

    def align_guide_tree(self, guide):
        """takes in a tupled guide tree and aligns starting from inner most node"""
        from openclean.profiling.pattern.align.NJ_Cluster import list_contains_list

        def traverse(o, func):
            """traverses the order array finding the deepest node"""
            for item in o:
                if isinstance(item, str) or isinstance(item, tuple):
                    yield item
                if isinstance(item, list):
                    if not list_contains_list(item):
                        a, _ = func(item)
                        yield a
                    else:
                        yield list(traverse(item, func))

        def apply_func(order, func):
            """perform the func starting with the inner most list moving outwards till no inner list remains"""
            while list_contains_list(order):
                order = list(traverse(order, func))
            return func(order)

        return apply_func(guide, self.align_column)

    def align(self, x, y):
        """align a sequence with the alignment"""
        x = [x] if isinstance(x, str) else list(x) if isinstance(x, Iterable) else None
        y = [y] if isinstance(y, str) else list(y) if isinstance(y, Iterable) else None

        if x is None or y is None:
            raise ValueError("Invalid input.")

        if len(x) == 1 and len(y) == 1:
            alignment, F = self.pairwise.align(x[0], y[0], keep_gaps_together=self.keep_gaps_together)
            ax = [self.resolve_alignment(x[0], alignment, left=True)]
            ax.append(self.resolve_alignment(y[0], alignment, left=False))
            return tuple(ax), F

        DIAG = -1, -1
        LEFT = -1, 0
        UP = 0, -1

        # Create tables F and Ptr and get costing
        Ptr = {}

        aln = self.get_pairs(x)
        seq = self.get_pairs(y)
        N = len(aln) - 1
        M = len(seq) - 1

        F = self.init_matrix(aln, seq)

        option_Ptr = DIAG, LEFT, UP

        for i, j in product(range(M), range(N)):
            option_F = (
                F[i - 1, j - 1] + self.pairwise_dist(aln[j], seq[i]),
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

        aligned = list()
        for xi in x:
            res = self.resolve_alignment(xi, alignment, left=False)
            aligned.append(res)

        for yi in y:
            res = self.resolve_alignment(yi, alignment, left=True)
            aligned.append(res)

        return tuple(aligned), F

    def align(self, column, groups):
        """



        Parameters
        ----------
        column: list[Tuple(Tokens)]
            The column to align
        groups: dict
            The dict of groups with group id as key and row indices as values
        Returns
        -------
            list[Tuple(Tokens)]
        """
        raise NotImplementedError()
