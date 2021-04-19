# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Class to calculate absolute distance between row lengths"""

from openclean_pattern.align.distance.base import Distance

DISTANCE_ABSOLUTE = 'ABS'


class AbsoluteDistance(Distance):
    """Class computes the absolute distance between row lengths"""

    def __init__(self):
        """Initialize the class"""
        super(AbsoluteDistance, self).__init__(DISTANCE_ABSOLUTE)

    def compute(self, u, v):
        """
        Takes 2 rows and calculates the distance (float) between them

        Parameters
        ----------
        u: tuple[Tokens]
            row 1 in the comparison
        v: tuple[Tokens]
            row 2 in the comparison

        Return
        -------
            float
        """
        return abs(len(u) - len(v))
