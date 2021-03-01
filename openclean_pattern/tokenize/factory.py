# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Factory methods to instantiate a tokenizer class """

from openclean_pattern.tokenize.regex import RegexTokenizer, TOKENIZER_REGEX, DefaultTokenizer, TOKENIZER_DEFAULT


class TokenizerFactory(object):
    """factory methods to create a tokenizer class object
    """

    @staticmethod
    def create_tokenizer(tokenizer, type_resolver=None):
        """Returns the tokenizer class if the input string matches the tokenizer name

        Parameters
        ----------
        tokenizer: str
            name string of the tokenizer
        type_resolver: openclean_pattern.datatypes.resolver.TypeResolver (default: None)
            type resolvers to incorporate non-basic datatypes
        """
        if tokenizer == TOKENIZER_REGEX:
            return RegexTokenizer(type_resolver=type_resolver)
        elif tokenizer == TOKENIZER_DEFAULT:
            return DefaultTokenizer()

        raise ValueError('tokenizer: {} not found'.format(tokenizer))
