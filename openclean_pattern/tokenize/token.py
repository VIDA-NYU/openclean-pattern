# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.


class Token:
    '''
    internal representation of each token with key information intact
    '''
    def __init__(self, regex_type, size, value):
        self.regex_type = regex_type
        self.size = int(size)
        self.value = value

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
        return tuple([self.value, self.regex_type, self.size])
