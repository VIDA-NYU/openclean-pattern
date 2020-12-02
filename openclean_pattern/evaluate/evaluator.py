# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Pattern Evaluator class to evaluate regex patterns on new data"""


from openclean_pattern.regex.base import PatternElement, Pattern
from openclean_pattern.tokenize.token import Token
from openclean_pattern.datatypes.base import SupportedDataTypes


class Evaluator(object):
    """Class to contain different evaluation techniques / methods for patterns on new data"""
    @staticmethod
    def evaluate(pattern, value):
        """
        Parses through each token and returns False if any Token value.regex_type doesn't
        match the respective pattern.element_type

        Parameters
        ----------
        pattern : Pattern
            The pattern to evaluate against
        value : list[Token]
            The tokens of a single row to match with the pattern

        Returns
        -------
            bool

        Raises
        ------
            ValueError
        """
        if not isinstance(pattern, Pattern):
            raise ValueError("Invalid Pattern")

        value = [value] if not isinstance(value, tuple) else value

        for p, v in zip(pattern, value):
            if not isinstance(p, PatternElement):
                raise ValueError("Invalid PatternElemenet")
            elif not isinstance(v, Token):
                raise ValueError("Invalid Token")

            if p.element_type != v.regex_type.name:
                if p.element_type == SupportedDataTypes.ALPHANUM and\
                        (v.regex_type.name in [SupportedDataTypes.ALPHA, SupportedDataTypes.DIGIT]):
                    continue
                return False

        if len(pattern) != len(value):
            return False

        return True
