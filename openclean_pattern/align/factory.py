# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Factory methods to instantiate an alignment class """

from openclean_pattern.align.combinatorics import CombAligner, ALIGN_COMB
from openclean_pattern.align.group import GroupAligner, ALIGN_GROUP
from openclean_pattern.align.distance import DISTANCE_ETDE


class AlignerFactory(object):
    """factory methods to create an aligner class object
    """

    @staticmethod
    def create_aligner(aligner):
        """Returns the tokenizer class if the input string matches the tokenizer name

        Parameters
        ----------
        aligner: str
            name string of the aligner
        """
        if aligner == ALIGN_GROUP:
            return GroupAligner()
        elif aligner == ALIGN_COMB:
            return CombAligner()

        raise ValueError('aligner: {} not found'.format(aligner))
