# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.


from abc import ABCMeta, abstractmethod


class Aligner(metaclass=ABCMeta):
    """aligns the token objects and returns groups of aligned token groups"""

    def __init__(self, alignment_type):
        """intializes the Aligner object

        Parameters
        ----------
        alignment_type: str
            the align type to use to align the column tokens
        """
        self.alignment_type = alignment_type

    @abstractmethod
    def align(self, column):
        """the align method takes in a list of openclean_pattern.tokenize.token.Tokens and aligns them to minimize
        the distance between that row and the others. The returned object is a dict of lists with each inner list
         representing a group having the same no. of tokens / same cluster

        Parameters
        ----------
        column: list[openclean_pattern.tokenize.token.Token]
            the column to align

        Returns
        -------
            a dict of lists with key 'n' representing the length and each inner list representing row_indices of groups
             with n tokens / row_index of part of the cluster
        """
        raise NotImplementedError()
