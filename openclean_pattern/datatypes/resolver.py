# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Classes responsible for resolving various non-basic and basic data types into Tokens.
"""

from abc import abstractmethod, ABCMeta
from typing import Iterable, List, Optional, Tuple

import datamart_geo
import pandas as pd
import os
import sqlite3

from openclean.data.refdata import RefStore
from openclean_pattern.tokenize.prefix_tree import PrefixTree
from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean.function.token.base import Token, TokenTransformer

import openclean.function.token.base as TT

RESOURCES = '../../resources/data/'

MONTHS = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'Jun',
    'Jul',
    'Aug',
    'Sept',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
]

WEEKDAYS = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
    'Mon',
    'Tue',
    'Wed',
    'Thurs',
    'Fri',
    'Sat',
    'Sun'
]


class TypeResolver(TokenTransformer, metaclass=ABCMeta):
    """This class resolves different data types"""

    @abstractmethod
    def resolve(self, tokens: List[Token]) -> List[Token]:
        """returns the basic / non-basic data type augmented row. this can be a
        combination of str and openclean.function.token.base.Token's.

        Parameters
        ----------
        tokens: list of openclean.function.token.base.Token
            List of string tokens.

        Returns
        -------
        list of openclean.function.token.base.Token
        """
        raise NotImplementedError()  # pragma: no cover

    def transform(self, tokens: List[Token]) -> List[Token]:
        """The transform method of the token transformer is a synonym for the
        type resolve function.
        """
        return self.resolve(tokens=tokens)


class DefaultTypeResolver(TypeResolver):
    """ The DefaultTypeResolver to be used. The general idea here is to always have the BasicTypeResolver
    present and attach middleware TypeResolvers to add non-basic type resolution if needed. The order in which
    they are entered prioritizes between them. e.g. if DataTime takes preference over GeoSpatial, a
    county called March County would be identified as (_MONTH_, _ALPHA_ ) instead of ( _COUNTY_ )
    """

    def __init__(self, interceptors=None):
        """ Initializes the DefaultTypeResolver.

        Parameters
        ----------
        interceptors: List[TypeResolver]
            the type resolvers for non-basic resolution
        """
        if interceptors is None:
            interceptors = []

        if not isinstance(interceptors, list):
            if isinstance(interceptors, TypeResolver):
                interceptors = [interceptors]
            else:
                raise TypeError('expected a TypeResolver or a list of TypeResolvers. Got {}'.format(interceptors))

        interceptors.append(BasicTypeResolver())
        self.interceptors = interceptors

    def resolve(self, tokens: List[Token]) -> List[Token]:
        """passes through all the middlewares and adding found non-basic types and finally through the
        BasicTypeResolver.

        Parameters
        ----------
        tokens: list of openclean.function.token.base.Token
            List of string tokens.

        Returns
        -------
        list of openclean.function.token.base.Token
        """
        for mw in self.interceptors:
            tokens = mw.resolve(tokens)
        return tokens


class BasicTypeResolver(TypeResolver):
    """ Class to resolve to the supported basic types
            STRING = STRING_REP = '\\W+'
            ALPHA = ALPHA_REP = 'ALPHA'
            ALPHANUM = ALPHANUM_REP = 'ALPHANUM'
            DIGIT = DIGIT_REP = 'NUMERIC'
            PUNCTUATION = PUNCTUATION_REP = 'PUNC'
            GAP = 'G'
            SPACE_REP = '\\S'
            OPTIONAL_REP = '?'
    """

    def resolve(self, tokens: List[Token]) -> List[Token]:
        """Annotate tokens of type ANY with one of the default token types.

        Patameters
        ----------
        tokens: list of openclean.function.token.base.Token
            List of string tokens.

        Returns
        -------
        list of openclean.function.token.base.Token
        """
        resolved = list()
        for token in tokens:
            # Only consider tokens of type ANY
            if token.regex_type == TT.ANY:
                if token.isdigit():
                    token.regex_type = SupportedDataTypes.DIGIT
                elif token.isalpha():
                    token.regex_type = SupportedDataTypes.ALPHA
                elif token.isalnum():
                    token.regex_type = SupportedDataTypes.ALPHANUM
                elif token.isspace():
                    token.regex_type = SupportedDataTypes.SPACE_REP
                else:
                    token.regex_type = SupportedDataTypes.PUNCTUATION
            resolved.append(token)
        # Return modified token list.
        return resolved


class AdvancedTypeResolver(TypeResolver, metaclass=ABCMeta):
    """Non-basic type resolver. It lookups the prefix tree for a match and then returns the respective label.
    If it fails to find a good non-basic match for a token, it returns the str token value. The prefix tree exists
    to enhance performance
     """

    def __init__(self, vocabulary: Iterable[Tuple[Iterable[str], str]], ignore_case: Optional[bool] = True):
        """initializes the prefix tree

        Parameters
        ----------
        vocabulary: Iterable
            Vocabulary to build tree from. Different lists of words in the
            vocabulary are associated with a type label.
        ignore_case: bool, default=True
            Perform case-insensitive matching if True.
        """
        self.pt = PrefixTree(vocabulary=vocabulary, ignore_case=ignore_case)

    def find_prefixes(self, tokens: List[Token]) -> List[Token]:
        """lookups tokens in prefix tree for matches and sorts the prefixes by descending order in no. of tokens

        Parameters
        ----------
        tokens: list of openclean.function.token.base.Token
            The tokens to search for in the prefix tree.

        Returns
        -------
        list of openclean.function.token.base.Token
        """
        result = list()
        while tokens:
            pidx, label = self.pt.prefix_search(tokens, ignore_punc=True)
            if pidx is None:
                result.append(tokens[0])
                pidx = 0
            else:
                value = ' '.join(tokens[:pidx + 1]).strip()
                token = Token(value=value, token_type=label, rowidx=tokens[0].rowidx)
                result.append(token)
            tokens = tokens[pidx + 1:]
        return result

    def resolve(self, tokens: List[Token]) -> List[Token]:
        """idenfifier non-basic data types in the tokenized_row and replaces them with Tokens.

        Patameters
        ----------
        tokens: list of openclean.function.token.base.Token
            List of string tokens.

        Returns
        -------
        list of openclean.function.token.base.Token
        """
        resolved = list()
        # Find prefix matches for each sublist of consecutive tokens of
        # type ANY.
        candidates = list()
        for token in tokens:
            if token.type() == TT.ANY:
                candidates.append(token)
            else:
                if len(candidates) > 0:
                    resolved.extend(self.find_prefixes(candidates))
                    candidates = list()
                resolved.append(token)
        if len(candidates) > 0:
            resolved.extend(self.find_prefixes(candidates))
        return resolved


class DateResolver(AdvancedTypeResolver):
    """Resolves date times."""

    def __init__(self, ignore_case: Optional[bool] = True):
        """Initializes the datetime resolver. Preloads data about weekdays and
        months and builds a prefix tree.

        Parameters
        ----------
        ignore_case: bool, default=True
            Perform case-insensitive matching if True.
        """
        super(DateResolver, self).__init__(
            vocabulary=[(WEEKDAYS, SupportedDataTypes.WEEKDAY), (MONTHS, SupportedDataTypes.MONTH)],
            ignore_case=ignore_case
        )


class GeoSpatialResolver(AdvancedTypeResolver):
    """Resolves geo spatial types"""

    def __init__(self, levels=None, ignore_case: Optional[bool] = True):
        """Initializes the geospatial resolver. Preloads data from datamart_geo and builds a prefix tree

        Parameters
        ----------
        levels: list or int
            list of levels to use from the datamart_geo library
        """
        # levels to use from the datamart_geo profiled
        if levels is None:
            levels = [0, 1, 2, 3, 4, 5]
        elif isinstance(levels, int):
            levels = [levels]
        elif isinstance(levels, list):
            for i in levels:
                if not isinstance(i, int):
                    raise ValueError('expected list of integers')
        else:
            raise ValueError('expected list or integers')

        # Download data
        # Note: We should try to use RefData here if possible. Also, the RESOURCES
        # folder will not be available when installing this as package!
        GEOPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), RESOURCES)
        datamart_geo.GeoData.download(GEOPATH, update=False)

        # Read sqlite query results into a pandas DataFrame
        con = sqlite3.connect(os.path.join(GEOPATH, 'admins.sqlite3'))
        geodata = pd.read_sql_query("SELECT name, level from admins", con)

        self.admins = list()
        for level in levels:
            data = geodata[geodata['level'] == level]['name'].str.lower().to_list()
            self.admins.append((data, self.get_label(level)))

        # Convert dataframe into vocabulary
        # self.areas = list()
        # for admin in self.admins:
        #     self.areas += admin

        # todo: pickle full tree?

        super(GeoSpatialResolver, self).__init__(self.admins)

    def get_label(self, value):
        labels = [SupportedDataTypes.ADMIN_LEVEL_0,
                  SupportedDataTypes.ADMIN_LEVEL_1,
                  SupportedDataTypes.ADMIN_LEVEL_2,
                  SupportedDataTypes.ADMIN_LEVEL_3,
                  SupportedDataTypes.ADMIN_LEVEL_4,
                  SupportedDataTypes.ADMIN_LEVEL_5]


        return labels[value]


class BusinessEntityResolver(AdvancedTypeResolver):
    """Resolves Business Entity Suffixes"""

    def __init__(self, ignore_case: Optional[bool] = True):
        """Initializes the business entity resolver. Preloads data about company suffixes and builds a prefix tree
        """
        # extracted using regex from https://www.harborcompliance.com/information/company-suffixes
        refdata = RefStore()
        values = refdata\
            .load('company_suffixes', auto_download=True)\
            .distinct('company_suffix')
        # Replace dots for all abbreviations
        business_suffixes = [v.replace('.', '').lower() for v in values]
        super(BusinessEntityResolver, self).__init__(
            vocabulary=[(set(business_suffixes), SupportedDataTypes.BE)]
        )


class AddressDesignatorResolver(AdvancedTypeResolver):
    """ Resolves street abbreviations and suds"""

    def __init__(self, ignore_case: Optional[bool] = True):
        """ initializes address designator resolver by preloading street and sud dat"""
        self.dtype = ''
        # https://pe.usps.com/text/pub28/28apc_002.htm
        refdata = RefStore()
        street = refdata.load('usps:street_abbrev', auto_download=True).df()
        street = set(street.fillna('').applymap(str.lower).values.flatten())
        street.discard('')
        street = set(street)
        vocabulary = [(street, SupportedDataTypes.STREET)]
        # https://pe.usps.com/text/pub28/28apc_003.htm
        sud = refdata.load('usps:secondary_unit_designators', auto_download=True).df()
        sud = set(sud.fillna('').applymap(str.lower).values.flatten())
        sud.discard('')
        vocabulary.append((set(sud).difference(street), SupportedDataTypes.SUD))
        super(AddressDesignatorResolver, self).__init__(vocabulary=vocabulary, ignore_case=ignore_case)
