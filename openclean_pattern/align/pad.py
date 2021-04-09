# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""implements a naive padding aligner"""

from openclean_pattern.datatypes.base import create_gap_token
from openclean_pattern.align.base import Aligner


ALIGN_PAD = "pad"


class Padder(Aligner):
    """Aligns using the most frequent tokens and minimum set coverage
    """

    def __init__(self):
        """Initializes the Padder"""
        super(Padder, self).__init__(ALIGN_PAD)

    def align(self, column, groups):
        """Takes in the column and the groups and returns an aligned version of each group by adding Gap tokens to each row.
        A list[Tuple(Tokens)] is returned with row indices that appeared together in the groups dict,
        are padded to the same no. of tokens per group

        Parameters
        ----------
        column: list[Tuple(Tokens)]
            The column to align
        groups: dict
            The dict of groups with group id as key and row indices as values
        Returns
        -------
            dict[int, Tuple(Tokens)]
        """
        aligned = [None] * len(column)
        for cluster, idx in groups.items():
            #  pad the smaller ones with gap characters
            col = list()
            size = 0
            for id in idx:
                if not isinstance(id, int):
                    raise KeyError("row indices should be int. found: {}".format(id))

                if len(column[id]) > size:
                    size = len(column[id])
                col.append(column[id])

            for c, id in zip(col, idx):
                while len(c) < size:
                    c = (*c, create_gap_token(rowidx=id))

                if aligned[id] is not None:
                    raise KeyError("found duplicate aligned tokens({new} and {old}) for same row id: {id}".format(id=id, new=c, old=aligned[id]))
                aligned[id] = c

        return aligned
