# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Base class for various tokenizers """

from abc import ABCMeta, abstractmethod


class Tokenizer(object, metaclass=ABCMeta):
    """ Tokenizer abstract class that enables strings to be broken down and Typechecked.
     It has multiple functions not limited to:
        - Replace strings with non-basic data types using TypeResolving encoders
        - Replace special characters
        - Tokenize on specified delimiters
    It accepts a list of strings and returns a list of tokenized tuples
    """
    def __init__(self, tokenizer_name, type_resolver=None, case=str.lower):
        """Initializes the Tokenizer

        Parameters
        ----------
        tokenizer_name: str
            name of the tokenizer used by the tokenizer factory
        type_resolver: openclean_pattern.datatypes.resolver.TypeResolver (default: None)
            type resolvers to incorporate non-basic and basic datatypes
        case: Callable (default: str.lower)
            changes all values to this case. Incase the type resolver uses a prefix tree trained on preset vocabulary,
            the case of the tokens should match with the case here.
        """
        self.tokenizer_name = tokenizer_name
        self.type_resolver = type_resolver
        self.case = case

    @abstractmethod
    def _tokenize_value(self, rowidx, value):
        """tokenizes individual values

        Parameters
        ----------
        rowidx: int
            row id
        value: str
            the value to tokenize

        Returns
        -------
            tuple of tokens
        """
        raise NotImplementedError()

    @abstractmethod
    def _encode_value(self, rowidx, value):
        """ tokenizes a single row value and then passes the token rows to the underlying TypeResolver
        to convert the tokens to their equivalent internal regex representations

        Parameters
        ----------
        rowidx: int
            row id
        value: str
            value to tokenize

        Returns
        -------
        tuple of openclean.function.token.base.Token
        """
        raise NotImplementedError()

    def tokenize(self, column):
        """tokenizes the column

        Parameters
        ----------
        column: list of lists/tuples
            list of column values

        Returns
        -------
            list of tupled tokens
        """
        tokenized = list()
        for rowidx, value in enumerate(column):
            value = value[0] if isinstance(value, list) or isinstance(value, tuple) else value
            tokenized.append(self._tokenize_value(rowidx=rowidx, value=value))
        return tokenized

    def encode(self, column):
        """encodes the columns into their type representations and tokenizes each value

        Parameters
        ----------
        column: list of lists/tuples
            list of column values
        func: Callable (default:tokenize_value)
            callable to execute on the column. Could be just tokenizing the values (default) or encoding them

        Returns
        -------
        list of tupled tokens
        """
        encoded = list()
        for rowidx, value in enumerate(column):
            value = value[0] if isinstance(value, list) or isinstance(value, tuple) else value
            encoded.append(self._encode_value(rowidx=rowidx, value=value))
        return encoded
