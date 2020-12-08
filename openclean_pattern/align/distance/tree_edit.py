# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Class to compute Tree edit distances for alignment"""

from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.align.distance.base import Distance


DISTANCE_TED = 'TED'


class TreeEditDistance(Distance):
    """Takes in two rows of Tokens and calculates the distance between them"""
    def __init__(self):
        """Initializes the distance class"""
        super(TreeEditDistance, self).__init__(DISTANCE_TED)

    # distance b/w 2 rows:
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
        distance = 0
        puncs = [SupportedDataTypes.SPACE_REP, SupportedDataTypes.PUNCTUATION]

        # zip same positioned tokens
        for ui, vi in zip(u, v):
            # if they are of different types
            if ui.regex_type != vi.regex_type:
                # and both are not punctuation
                if ui.regex_type in puncs and vi.regex_type in puncs:
                    continue
                # increment the distance
                distance += 1

        # get the normalization denominator and add no. of gaps to the distance
        bigger = u if len(u) > len(v) else v
        gaps = abs(len(u)-len(v))
        distance += gaps

        # return normalized distance
        return distance/len(bigger)
