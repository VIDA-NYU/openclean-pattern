# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Aligner class which naively groups by similar tokens and returns the groups"""

from openclean_pattern.align.base import Aligner

from collections import defaultdict

ALIGN_GROUP = "group"


class GroupAligner(Aligner):
    """This aligner creates groups based on the no. of tokens in each group"""
    def __init__(self):
        """intializes the Aligner object
        """
        super(GroupAligner, self).__init__(ALIGN_GROUP)


    def align(self, column):
        """the align method takes in a list of openclean_pattern.tokenize.token.Tokens and aligns them to minimize
        the distance between that row and the others. The returned object is a dict of lists with each inner list
        representing a group having the same no. of tokens

        Parameters
        ----------
        column: list of list[openclean_pattern.tokenize.token.Token]
            the column to align

        Returns
        -------
             a dict of lists with key 'n' representing the length and each inner list representing row_indices of groups
             with n tokens / row_index of part of the cluster
       """
        groups = defaultdict()
        for i, row in enumerate(column):
            n = len(row)
            if n not in groups:
                groups[n] = list()
            groups[n].append(i)

        return groups
