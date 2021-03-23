# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

from openclean_pattern.datatypes.base import SupportedDataTypes

class Token(str):
    '''
    internal representation of each token with key information intact
    '''
    def __new__(cls, value, *args, **kwargs):
        # explicitly only pass value to the str constructor because strs are mutable and wont support other attributes
        return super(Token, cls).__new__(cls, value)

    def __init__(self, regex_type: SupportedDataTypes, value: str, rowidx: int):
        """initialize the Token object

        Parameters
        ----------
        regex_type: openclean_pattern.datatypes.base.SupportedDataTypes
            the type and representation of the Token
        value: str
            the string value
        rowidx: int
            the row index
        """
        self.regex_type = regex_type
        self.size = len(value)
        self.value = value
        self.rowidx = rowidx

    def __repr__(self):
        return f'_{self.regex_type.value!r}_({self.size!r},{self.value!r})'

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.regex_type == other.regex_type \
               and self.size == other.size \
               and self.value == other.value

    def __str__(self):
        return self.__repr__()

    def to_tuple(self):
        """returns a tuple of the string, type and size
        """
        return tuple([self.value, self.regex_type, self.size])
