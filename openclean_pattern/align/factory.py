# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Factory methods to instantiate an alignment class """

from openclean_pattern.align.combinatorics import CombAligner, ALIGN_COMB
from openclean_pattern.align.pad import ALIGN_PAD, Padder


class AlignerFactory(object):
    """factory methods to create an aligner class object
    """

    @staticmethod
    def create_aligner(aligner):
        """Returns the aligner instance if the input string matches an aligner name

        Parameters
        ----------
        aligner: str
            name string of the aligner
        """
        if aligner == ALIGN_PAD:
            return Padder()
        #todo: fix combAligner
        elif aligner == ALIGN_COMB:
            return CombAligner()

        raise ValueError('aligner: {} not found'.format(aligner))
