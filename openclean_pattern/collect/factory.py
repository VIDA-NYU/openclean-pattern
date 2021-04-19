# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Factory methods to instantiate a Collector class """

from openclean_pattern.collect.group import Group, COLLECT_GROUP
from openclean_pattern.collect.cluster import Cluster, COLLECT_CLUSTER
from openclean_pattern.collect.neighbor import NeighborJoin, COLLECT_NEIGHBOR
from openclean_pattern.collect.base import Collector


class CollectorFactory(object):
    """factory methods to create an collector object
    """

    @staticmethod
    def create_collector(collector: str, **kwargs) -> Collector:
        """Returns the collector object if the input string matches a collector name

        Parameters
        ----------
        collector: str
            name string of the collector
        """
        if collector == COLLECT_GROUP:
            return Group()
        elif collector == COLLECT_CLUSTER:
            return Cluster(**kwargs)
        elif collector == COLLECT_NEIGHBOR:
            return NeighborJoin()

        raise ValueError('collector: {} not found'.format(collector))
