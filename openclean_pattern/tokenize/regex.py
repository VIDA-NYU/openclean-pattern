# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

from openclean_pattern.tokenize.base import Tokenizer
from openclean_pattern.datatypes.resolver import DefaultTypeResolver
from openclean_pattern.datatypes.resolver import TypeResolver
import re

TOKENIZER_REGEX = 'punc'


class RegexTokenizer(Tokenizer):
    """The RegexTokenizer tokenizes the input list using all punctuation delimiters and keeps them intact by default.
    It also breaks down the word character '_'. A user is allowed to supply a different regex expression.
    The encoding method passes the tokenized strings to the underlying type resolver to generate the equivalent
    internal representation of openclean_pattern.tokenize.token objects.
    """

    def __init__(self, regex=r"[\w]+|[^\w]", type_resolver=None, abbreviations=False):
        """initializes the tokenizer.

        Parameters
        ----------
        regex: str
            the regular expression to tokenize on
        type_resolver: openclean_pattern.datatypes.resolver.TypeResolver (default: None)
            type resolvers to incorporate compound datatypes
        abbreviations: bool (default: False)
            by default, the content string is tokenized on all punctuation. If True, dots
            will not be included as a tokenizing delimiter as they represent abbreviations. A user
            provided regex will take precedence over the abbreviations even if it is set to True
        """
        super(RegexTokenizer, self).__init__(TOKENIZER_REGEX, type_resolver)
        if abbreviations and regex == r"[\w]+|[^\w]":
            regex = r"[\w.]+|[^\w.]"
        self.regex = regex
        self.abbreviations = abbreviations

    def _tokenize_value(self, rowidx, value):
        """ tokenizes a single row value by applying the regular expression splitter.
        if abbreviations == True, the dots will be stripped at this stage to type_recognize the initials together
        furthermore we split on underscores as they are considered as \w characters in regex

        Parameters
        ----------
        rowidx: int
            row id
        value: str
            value to tokenize

        Returns
        -------
            tuple of strs
        """
        post_regex = re.findall(self.regex, self.case(value))

        if self.abbreviations:
            abbreviation_updated = list()
            for tok in post_regex:
                # ignore lone . characters
                if tok != '.' and tok.find('.') > -1:
                    tok = tok.replace('.', '')
                abbreviation_updated.append(tok)
            post_regex = abbreviation_updated

        return tuple([item for sublist in [re.split('(_)', j) for j in post_regex] for item in sublist])

    def _encode_value(self, rowidx, value):
        """ tokenizes a single row value using the tokenize_value method. Then pass the token rows to
        the underlying TypeResolver to convert the tokens to their equivalent internal regex representations.

        Parameters
        ----------
        rowidx: int
            row id
        value: str
            value to tokenize

        Returns
        -------
            tuple of openclean_pattern.tokenize.tokens
        """
        if not isinstance(self.type_resolver, TypeResolver):
            raise RuntimeError("type_resolver: {} not of type: DataTypeResolver".format(type(self.type_resolver)))
        val = self._tokenize_value(rowidx, value)
        encoded = self.type_resolver.resolve_row(rowidx, val)
        return tuple(encoded)


TOKENIZER_DEFAULT = 'default'


class DefaultTokenizer(RegexTokenizer):
    """Default tokenizer class that splits on all punctuation and only encodes values into atomic types. More aptly,
    it is a use case of the RegexTokenizer"""

    def __init__(self):
        """initializes the tokenizer with the DefaultTpeResolver without any interceptors"""
        super(DefaultTokenizer, self).__init__(type_resolver=DefaultTypeResolver())
