# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Collector class which naively groups by similar tokens and returns the groups"""

from openclean_pattern.collect.base import Collector

from collections import defaultdict

COLLECT_GROUP = "group"


class Group(Collector):
    """This collector creates groups based on the no. of tokens in each group"""
    def __init__(self):
        """intializes the collector object
        """
        super(Group, self).__init__(COLLECT_GROUP)

    def collect(self, column):
        """The collect method takes in a list of openclean.function.token.base.Token's
        and aligns them to minimize the distance between that row and the others.
        The returned object is a dict of lists with each inner list representing
        a group having the same no. of tokens.


        Parameters
        ----------
        column: list of iterable[openclean.function.token.base.Token]
            the column to align

        Returns
        -------
        a dict of lists with key 'n' representing the cluster and each inner
        list representing row_indices of groups with n tokens / row_index of
        part of the cluster.
        """
        groups = defaultdict()
        for i, row in enumerate(column):
            n = len(row)
            if n not in groups:
                groups[n] = list()
            groups[n].append(i)

        return groups
