# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Predicates that test whether a pattern expression matches a given input
string.
"""


from openclean.function.value.base import PreparedFunction


class IsMatch(PreparedFunction):
    """Matches strings against given patterns"""
    def __init__(
        self, func, negated=False, **kwargs
    ):
        """Initialize the class based on if pattern is str or Pattern.

        If str, the re library is invoked to process the pattern matching.
        The full match flag determines whether the pattern has to match
        input strings completely or only partially. The type case flag
        determines whether values that are not of type string are converted
        to string or ignored.

        If Pattern, the openclean_pattern library is invoked to process the
        pattern matching. A patternfinder parameter is desirable to be able
        to recreate the steps (tokenization / non basic type detection etc)
        that went into the pattern generation process. If all tokens of the
        value match with the respective pattern element, the returned
        predicate is True, else False.

        Parameters
        ----------
        func: Callable
            Pattern Expression compare method.
        negated: bool, default=False
            Negate the return value of the function to check for values that
            are no matches for a given pattern.
        tokenizer: openclean_pattern.tokenizer.base.Tokenizer, default=None
            The steps used to create the pattern to perform on the value
        """
        if not callable(func):
            raise TypeError("Invalid Comparator")
        self.func = func
        self.negated = negated
        self.tokenizer = kwargs.get("tokenizer")

    def eval(self, value):
        """Match the regular expression against the given string. If the value
        is not of type string it is converted to string if the type case flag
        is True. Otherwise, the result is False.

        Parameters
        ----------
        value: string
            Input value that is matched against the regular expression.

        Returns
        -------
        bool
        """
        return self.func(value=value, tokenizer=self.tokenizer) != self.negated


class IsNotMatch(IsMatch):
    """Match strings against a given regular expression. Returns True if the
    value does not match the expression.
    """
    def __init__(self, func, **kwargs):
        """Initialize the regular expression pattern. The full match flag
        determines whether the pattern has to match input strings completely
        or only partially. The type case flag determines whether values that
        are not of type string are converted to string or ignored.

        Parameters
        ----------
        func: Callable
            Pattern Expression compare method.
        tokenizer: openclean_pattern.tokenizer.base.Tokenizer, default=None
            The steps used to create the pattern to perform on the value
        """
        super(IsNotMatch, self).__init__(
            func=func,
            negated=True,
            tokenizer=kwargs.get('tokenizer')
        )
