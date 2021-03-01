# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Distances to be used for alignment"""

from abc import ABCMeta, abstractmethod


class Distance(object, metaclass=ABCMeta):
    """Distances interface to use for alignment
    """
    def __init__(self, dist):
        """Initialize the class

        Parameters
        ----------
        dist: str
            the distance type
        """
        self.dist_type = dist

    @abstractmethod
    def compute(self, u, v):
        """
        Takes 2 rows and calculates the distance (float) between them

        Parameters
        ----------
        u: list[Tokens]
            row 1 in the comparison
        v: list[Tokens]
            row 2 in the comparison

        Return
        -------
            float
        """
        raise NotImplementedError()