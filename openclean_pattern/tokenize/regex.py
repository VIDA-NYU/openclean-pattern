# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

from typing import Callable, List, Optional

import re

from openclean.data.types import Scalar
from openclean.function.token.base import Token, Tokenizer
from openclean_pattern.datatypes.resolver import DefaultTypeResolver, TypeResolver

TOKENIZER_REGEX = 'punc'


class RegexTokenizer(Tokenizer):
    """The RegexTokenizer tokenizes the input list using all punctuation
    delimiters and keeps them intact by default. It also breaks down the word
    character '_'. A user is allowed to supply a different regex expression.
    The encoding method passes the tokenized strings to the underlying type
    resolver to generate the equivalent internal representation of
    ``openclean.function.token.base.Token`` objects.
    """
    def __init__(
        self, regex: Optional[str] = r"[\w]+|[^\w]",
        type_resolver: Optional[TypeResolver] = None,
        abbreviations: Optional[bool] = False, case: Optional[Callable] = str.lower
    ):
        """Initializes the tokenizer.

        Parameters
        ----------
        regex: str
            the regular expression to tokenize on
        type_resolver: openclean_pattern.datatypes.resolver.TypeResolver (default: None)
            type resolvers to incorporate non-basic datatypes
        abbreviations: bool (default: False)
            by default, the content string is tokenized on all punctuation. If True, dots
            will not be included as a tokenizing delimiter as they represent abbreviations. A user
            provided regex will take precedence over the abbreviations even if it is set to True
        case: Callable (default: str.lower)
            changes all values to this case. Incase the type resolver uses a prefix tree trained on preset vocabulary,
            the case of the tokens should match with the case here.
        """
        self.tokenizer_name = TOKENIZER_REGEX
        self.type_resolver = type_resolver
        self.case = case
        if abbreviations and regex == r"[\w]+|[^\w]":
            regex = r"[\w.]+|[^\w.]"
        self.regex = regex
        self.abbreviations = abbreviations

    def tokens(self, value: Scalar, rowidx: Optional[int] = None) -> List[Token]:
        """ tokenizes a single row value by applying the regular expression splitter.
        if abbreviations == True, the dots will be stripped at this stage to type_recognize the initials together
        furthermore we split on underscores as they are considered as \\w characters in regex

        Parameters
        ----------
        rowidx: int
            row id
        value: str
            value to tokenize

        Returns
        -------
        list of openclean.function.token.Token
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

        tokens = [Token(value=item, rowidx=rowidx) for sublist in [re.split('(_)', j) for j in post_regex] for item in sublist]

        if self.type_resolver is not None:
            tokens = self.type_resolver.resolve(tokens)

        return tokens


TOKENIZER_DEFAULT = 'default'


class DefaultTokenizer(RegexTokenizer):
    """Default tokenizer class that splits on all punctuation and only encodes
    values into basic types. More aptly, it is a use case of the RegexTokenizer.
    """
    def __init__(self):
        """initializes the tokenizer with the DefaultTpeResolver without any interceptors"""
        super(DefaultTokenizer, self).__init__(type_resolver=DefaultTypeResolver())
