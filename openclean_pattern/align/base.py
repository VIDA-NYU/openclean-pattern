# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
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
    def align(self, column, groups):
        """Takes in the column and the groups and returns an aligned version of each group by adding Gap tokens to each row.
        A list[Tuple(Tokens)] is returned with the aligned values

        Parameters
        ----------
        column: list[Tuple(Tokens)]
            The column to align
        groups: dict
            The dict of groups with group id as key and row indices as values
        Returns
        -------
            list[Tuple(Tokens)]
        """
        raise NotImplementedError()
