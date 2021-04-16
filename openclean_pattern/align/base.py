# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.


from abc import ABCMeta, abstractmethod
from openclean_pattern.datatypes.base import create_gap_token
from openclean.function.token.base import Token

from typing import List, Dict, Tuple, Any


class Aligner(metaclass=ABCMeta):
    """Aligns the token objects and returns groups of aligned token groups"""

    def __init__(self, alignment_type: str):
        """intializes the Aligner object

        Parameters
        ----------
        alignment_type: str
            the align type to use to align the column tokens
        """
        self.alignment_type = alignment_type

    @abstractmethod
    def align(self, column, groups):
        """Takes in the column and the groups and returns an aligned version of
        each group by adding Gap tokens to each row.

        A list[Tuple(Tokens)] is returned with the aligned values

        Parameters
        ----------
        column: List[List(Tokens)]
            The column to align
        groups: dict
            The dict of groups with group id as key and row indices as values
        Returns
        -------
            dict[int, Tuple(Tokens)]
        """
        raise NotImplementedError()  # pragma: no cover


class Sequence(tuple):
    """A sequence of tokens"""
    def __init__(self, obj: Any):
        """initializes the Sequence of tokens, obj is consumed by the parent class

        Parameters
        ----------
        obj: Any
            object to create a tuple from. Consumed by the tuple class
        """
        super(Sequence, self).__init__()

    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        """accepts a list of tokens and creates a Sequence object

        Parameters
        ----------
        tokens: List[Token]
            the list of tokens to create a sequence from
        """
        toks = list()
        for t in tokens:
            toks.append(t)
        return cls(toks)

    def insert_gap(self, position: int):
        """inserts a gap at the specified position in the sequence

        Parameters
        ----------
        position: int
            0-indexed position to insert the gap
        """
        s = list()
        for i, token in enumerate(self):
            if position == i:
                s.append(create_gap_token())
            s.append(self[i])
        if position > len(self)-1:
            s.append(create_gap_token())

        return Sequence(s)


class Alignment(tuple):
    """A computed alignment from sequences"""
    def __init__(self, obj: Any):
        """initializes the Alignment object

        Parameters
        ----------
        obj: Any
            passed to the tuple class
        """
        super(Alignment, self).__init__()

    @classmethod
    def from_sequences(cls, seq: List[Sequence]):
        """creates an Alignment object using a list of sequences

        Parameters
        ----------
        seq: List[Sequence]
            the list of seq to convert into an Alignment object
        """
        sequences = list()
        for s in seq:
            sequences.append(s)
        return cls(sequences)

    @classmethod
    def from_tuple(cls, tup: Tuple):
        """creates an alignment object from a tuple containing either sequences or alignments or a combination of both

        Parameters
        ----------
        tup: Tuple
            the tuple to create an alignment from
        """
        alns = list()
        for t in tup:
            if isinstance(t, Alignment):
                for sq in t:
                    alns.append(sq)
            elif isinstance(t, Sequence):
                alns.append(t)
            else:
                raise ValueError("tuple should only either include Alignments or Sequences")

        return cls(alns)

    def insert_gap(self, position: int):
        """
        will insert a gap at the specified position in all sequences in the alignment

        Parameters
        ----------
        position: int
            0-indexed position to insert the gap in each sequence
        """
        copy = list()
        for sequence in self:
            copy.append(sequence.insert_gap(position))

        return Alignment(copy)
