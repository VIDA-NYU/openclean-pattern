# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""aligns the column Tokens by analyzing all possible combinations to reduce the distance"""

from openclean_pattern.align.base import Aligner

# from openclean_pattern.align.distance import DISTANCE_TDE, DISTANCE_ETDE
# from openclean_pattern.align.distance.factory import DistanceFactory
#
# import os, concurrent, csv, math, ast
# import numpy as np

# from openclean_pattern.regex.regex_objects import RegexToken, RegexRow
# from openclean_pattern.datatypes.base import SupportedDataTypes


# ALIGNER_COMB_PERM = 'perm'
# ALIGNER_COMB_COMB = 'comb'
#
# ALIGNER_COMB_SUPPORTED = [ALIGNER_COMB_PERM, ALIGNER_COMB_COMB]


ALIGN_COMB = 'comb'


class CombAligner(Aligner):
    """ looks at all the possible combinations of each token in each row with other all other rows,
    calculates the distance, clusters the closest alignments together using DBSCAN and returns the clustered groups.

    * Not recommended for large datasets or cases where the number of combinations between
    rows is too large (e.g. one row has 16 tokens and other has 6, the total no. of distance computation just for
    this combination would be 16P6 =  5765760)
    """
    def __init__(self):
        """intializes the Aligner object

        Parameters
        ----------
        alignment_type: str
            the align type to use to align the column tokens
        """
        super(CombAligner, self).__init__(ALIGN_COMB)

    def align(self, column, groups):
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
            list[Tuple(Tokens)]
        """
        raise NotImplementedError()
