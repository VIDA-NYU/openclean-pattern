# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Collector class which clusters similar tokens and returns the clusters"""

from openclean_pattern.collect.base import Collector
from openclean_pattern.align.distance.factory import DistanceFactory
from openclean_pattern.align.distance.tree_edit import DISTANCE_TED
from openclean.function.token.base import Token

from collections import defaultdict
from sklearn.cluster import DBSCAN
import numpy as np

from typing import List, Dict

COLLECT_CLUSTER = "cluster"


class Cluster(Collector):
    """This collector creates groups based on the clustering of similarly distanced tokens"""
    def __init__(self, dist=DISTANCE_TED, **kwargs):
        """intializes the collector object
        """
        super(Cluster, self).__init__(COLLECT_CLUSTER)
        self.distance = DistanceFactory.create(dist)
        self.eps = kwargs.get("eps", .1)
        self.min_samples = kwargs.get("min_samples", 5)

    def _precompute_distance(self, column: List[List[Token]]) -> np.array:
        """Accepts a n length column of tokens and generates a nxn matrix of all pairwise distances

         Parameters
         ----------
            column: list[list(Token)]

        Returns
        -------
            nxn numpy array
        """
        num_tokens = len(column)
        distances = np.empty((num_tokens, num_tokens))
        for u in range(num_tokens):
            # compute only half of the distances
            for v in range(u, num_tokens):
                distances[u][v] = distances[v][u] = self.distance.compute(column[u], column[v])
        return distances

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
        distances = self._precompute_distance(column)
        clustering = DBSCAN(
            metric="precomputed",
            n_jobs=-1,
            eps=self.eps,
            min_samples=self.min_samples
        ).fit(distances)

        groups = defaultdict()
        for i, n in enumerate(clustering.labels_):
            if n not in groups:
                groups[n] = list()
            groups[n].append(i)

        return groups
