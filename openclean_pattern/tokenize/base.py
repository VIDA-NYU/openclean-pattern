# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Base class for various tokenizers """

from abc import ABCMeta, abstractmethod

import string, re

class Tokenizer(object, metaclass=ABCMeta):
    """ Tokenizer abstract class that enables strings to be broken down and Typechecked.
     It has multiple functionas not limited to:
        - Replace strings with Compound data types using TypeResolving encoders
        - Replace special characters
        - Tokenize on specified delimiters
    It accepts a list of strings and returns a list of tokenized tuples
    """
    def __init__(self, tokenizer_name, type_resolver=None):
        """Initializes the Tokenizer

        Parameters
        ----------
        tokenizer_name: str
            name of the tokenizer used by the tokenizer factory
        type_resolver: openclean_pattern.datatypes.resolver.TypeResolver (default: None)
            type resolvers to incorporate compound and atomic datatypes
        """
        self.tokenizer_name = tokenizer_name
        self.type_resolver = type_resolver

    @abstractmethod
    def tokenize_value(self, value):
        """tokenizes individual values

        Parameters
        ----------
        value: str
            the value to tokenize

        Returns
        -------
            tuple of tokens
        """
        raise NotImplementedError()

    @abstractmethod
    def encode_value(self, column, freq):
        """returns an encoded regex matrix and it's stringified version

        Parameters
        ----------
        column: list
            list of column values
        freq: dict
            dict of frequencies

        Returns
        -------
            list of RegexRows, list of strings
        """
        raise NotImplementedError()

    def tokenize(self, column, func=tokenize_value):
        """tokenizes the column

        Parameters
        ----------
        column: list
            list of column values
        func: Callable (default:tokenize_value)
            callable to execute on the column. Could be just tokenizing the values (default) or encoding them

        Returns
        -------
            list of tupled tokens
        """
        tokenized = list()
        for value in column:
            tokenized.append(func(value))
        return tokenized

    def encode(self, column):
        """encodes the columns into their type representations and tokenizes each value

        Parameters
        ----------
        column: list
            list of column values
        func: Callable (default:tokenize_value)
            callable to execute on the column. Could be just tokenizing the values (default) or encoding them

        Returns
        -------
        list of tupled tokens
        """
        return self.tokenize(column, self.encode_value)


TOKENIZER_DEFAULT = 'default'


class DefaultTokenizer(Tokenizer):
    """Default tokenizer class that tokenizes on all punctuation and doesn't encode values into compound types"""
    def __init__(self, type_resolver=None):
        """initializes the tokenizer"""
        super(DefaultTokenizer, self).__init__(TOKENIZER_DEFAULT, type_resolver)

    def tokenize_value(self, value):
        """tokenizes individual values

        Parameters
        ----------
        value: str
            the value to tokenize

        Returns
        -------
            tuple of tokens
        """
        return re.split(string.punctuation, value)

    def encode_value(self, value):
        return tuple(self.tokenize_value(value))
