# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""implements the smart aligner"""


from openclean_pattern.align.base import Aligner

from collections import defaultdict

ALIGN_MSC = "msc"


class MSCAligner(Aligner):
    """Aligns using the most frequent tokens and minimum set coverage
    """
    def __init__(self):
        """initializes the Minimum Set Coverage Aligner
        """
        super(MSCAligner, self).__init__(ALIGN_MSC)

    def align(self, column):
        """ Looks at most frequent tokens at each position in the column, gets the minimum set coverage, and aligns
         everything according to it

        ROW ID | VALUE
        ----------------------------------------
        1       23        Jay         Allen   St
        2       245       Mercer      St
        3       -         Allen       St
        4       -         5th         Ave
        5       -         7th         Ave
        6       234       Broadway


        St -> {1, 2, 3}
        Ave -> {4, 5}
        Jay -> {1}


        Parameters
        ----------
        column: list of list[openclean_pattern.tokenize.token.Token]
            the column to align

        Returns
        -------
             a dict of lists with key 'n' representing the cluster and each inner list representing row_indices of groups
             that are part of the cluster
       """
        raise NotImplementedError()