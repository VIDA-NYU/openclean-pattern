# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

from openclean_pattern.tokenize.base import Tokenizer
from openclean_pattern.regex.compiler import RegexCompiler
from openclean_pattern.datatypes.resolver import DataTypeResolver
import re

TOKENIZER_REGEX = 'punc'


class RegexTokenizer(Tokenizer):
    """The RegexTokenizer tokenizes the input list using all punctuation delimiters and keeps them intact by default.
    A user should be able to supply a different regex expression.
    """
    def __init__(self, regex=r"[\w]+|[^\w]", type_resolver=None):
        """initializes the tokenizer.

        Parameters
        ----------
        regex: str
            the regular expression to tokenize on
        type_resolver: openclean_pattern.datatypes.resolver.TypeResolver (default: None)
            type resolvers to incorporate compound datatypes
        """
        super(RegexTokenizer, self).__init__(TOKENIZER_REGEX, type_resolver)
        self.regex = regex

    def tokenize_value(self, value):
        """ tokenizes a single row value by applying the regular expression splitter.
        furthermore splits on underscores (edgecase - not handled in the default regex)

        Parameters
        ----------
        value: str
            value to tokenize

        Returns
        -------
            tuple of tokens
        """
        x = re.findall(r"[\w]+|[^\w]", value)
        return (item for sublist in [re.split('(_)', j) for j in x] for item in sublist)

    def encode_value(self, value):
        if not isinstance(self, DataTypeResolver):
            raise RuntimeError("type_resolver: {} not of type: DataTypeResolver".format(type(self.type_resolver)))
        tokenized = list()
        val = self.tokenize_value(value)
        for token in val:
            tokenized.append(self.type_resolver.resolve(token))
        # return RegexCompiler.compile(col.tolist(), freq)
        return tuple(tokenized)
