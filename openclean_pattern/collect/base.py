# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.


from abc import ABCMeta, abstractmethod
from openclean_pattern.tokenize.token import Token

from typing import List, Dict


class Collector(metaclass=ABCMeta):
    """Collects the token objects and returns groups of similar token groups"""

    def __init__(self, collector_type: str):
        """intializes the Collector object

        Parameters
        ----------
        collector_type: str
            the collector type to use to collect the column tokens
        """
        self.collector_type = collector_type

    @abstractmethod
    def collect(self, column: List[List[Token]]) -> Dict[int, List]:
        """the collect method takes in a list of Tokens and collects similar rows using a collection strategy.
         The returned object is a dict of lists with each inner list representing a group of rows

        Parameters
        ----------
        column: list of list[Token]
            the column to align

        Returns
        -------
             a dict of lists with key 'n' representing the cluster and each inner list representing row_indices of groups
             with n tokens / row_index of part of the cluster
       """
        raise NotImplementedError()