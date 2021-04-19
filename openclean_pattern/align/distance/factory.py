# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Distances Factory to select between distances"""

from openclean_pattern.align.distance.absolute import AbsoluteDistance, DISTANCE_ABSOLUTE
from openclean_pattern.align.distance.tree_edit import TreeEditDistance, DISTANCE_TED


class DistanceFactory(object):
    '''
    factory methods to create a distance class object
    '''
    @staticmethod
    def create(distance: str = DISTANCE_TED):
        """returns the distance

        Returns
        -------
            Distance
        """
        """the distance to get using the factory

         Parameters
         ----------
         distance: str
             the distance type to create

         Returns
         -------
             Distance
         """
        if distance == DISTANCE_TED:
            return TreeEditDistance()
        elif distance == DISTANCE_ABSOLUTE:
            return AbsoluteDistance()
        else:
            raise ValueError(distance)
