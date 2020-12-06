# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""OpencleanPattern Evaluator class to evaluate regex patterns on new data"""


from openclean_pattern.regex.base import PatternElement, OpencleanPattern
from openclean_pattern.tokenize.token import Token
from openclean_pattern.datatypes.base import SupportedDataTypes


class Evaluator(object):
    """Class to contain different evaluation techniques / methods for patterns on new data"""
    @staticmethod
    def compare(pattern, value, generator):
        """Uses the default OpencleanPattern class' compare method. i.e. Parses through each token and
        returns False if any Token value.regex_type doesn't match the respective pattern.element_type

        Parameters
        ----------
        pattern : Pattern
            The pattern to evaluate against
        value : str or list[Token]
            The str value or tokens of a single row to match with the pattern
        generator: OpencleanPatternFinder
            a OpencleanPatternFinder object containing the type resolvers and tokenizers used to create
            the original pattern
        
        Returns
        -------
            bool

        Raises
        ------
            ValueError
        """
        if not isinstance(pattern, OpencleanPattern):
            raise ValueError("Invalid OpencleanPattern")

        return pattern.compare(value, generator)