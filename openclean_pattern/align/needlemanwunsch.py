# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""implements the NeedlemanWunschAligner"""

from openclean_pattern.align.base import Aligner
from openclean_pattern.datatypes.resolver import TypeResolver
from openclean_pattern.datatypes.base import SupportedDataTypes, create_gap_token
from openclean_pattern.align.distance.factory import DistanceFactory, DISTANCE_TED
from openclean_pattern.align.base import Sequence, Alignment

from collections import deque
from itertools import product
from typing import Iterable, List, Dict

ALIGN_NEEDLEMANWUNSCH = "nw"
GAP = SupportedDataTypes.GAP


class NeedlemanWunschAligner(Aligner):
    """
    Dynamic programming solution to the otherwise brute force sequence alignment problem vastly used for protien and nucleotide sequencing.
    Globally aligns two sequences at a time. Gap penalty and different initializations added here to allow different configurations.

    References
        https://www.cs.sjsu.edu/~aid/cs152/NeedlemanWunsch.pdf
        https://upload.wikimedia.org/wikipedia/en/c/c4/ParallelNeedlemanAlgorithm.pdf
    """

    def __init__(self, keep_gaps_together: bool = False):
        """initialize the NW aligner

        Parameters
        ----------
        keep_gaps_together: bool
            flag to allow different configurations

        """
        super(NeedlemanWunschAligner, self).__init__(ALIGN_NEEDLEMANWUNSCH)
        self.keep_gaps_together = keep_gaps_together
        self.dist = DistanceFactory.create(DISTANCE_TED)
        self.dist.strict = False

    def _align(self, x: Sequence, y: Sequence):
        """aligns two Sequences

        Parameters
        ----------
        x: Iterable
            value 1
        y: Iterable
            value 2

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
            F[i, -1] = -i if not self.keep_gaps_together else 2 * i
        for j in range(M):
            F[-1, j] = -j if not self.keep_gaps_together else 2 * j

        # heuristic optimal costing for sequences
        _eval = (lambda a, b: int(self.dist.compute([a], [b]) == 0)) if not self.keep_gaps_together else (
            lambda a, b: 2 if self.dist.compute([a], [b]) == 0 else -3)

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

        return list(alignment)

    def align(self, column: List, groups: Dict = None):
        if len(column) > 2 or groups is not None:
            raise ValueError("NeedlemanWunsch aligner only aligns two sequences")

        x, y = column[0], column[1]
        alignment = self._align(x, y)

        a, b = list(), list()
        for i, _ in alignment:
            if i is GAP:
                a.append(create_gap_token(i))
            else:
                a.append(x[i])

        for _, j in alignment:
            if j is GAP:
                b.append(create_gap_token(j))
            else:
                b.append(y[j])

        # return a, b
        return Alignment.from_sequences([Sequence(a), Sequence(b)])
