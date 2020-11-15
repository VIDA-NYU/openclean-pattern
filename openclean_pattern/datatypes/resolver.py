# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Classes responsible for resolving various compound and atomic data types into Tokens.
"""

import pandas as pd, os, datamart_geo, re

from openclean_pattern.tokenize.prefix_tree import PrefixTree
from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.tokenize.token import Token

from abc import abstractmethod, ABCMeta


class TypeResolver(metaclass=ABCMeta):
    """This class resolves different data types"""

    def resolve(self, column):
        """resolves the rows in the column into their type representations

        Parameters
        ----------
        column: list of lists/tuples of [str, openclean_patter.tokenize.token.Tokens]
            list of column values
        Returns
        -------
        list of tupled tokens
        """
        encoded = list()
        for value in column:
            if isinstance(value, str):
                value = [value]
            if not isinstance(value, list) and not isinstance(value, tuple):
                raise ValueError("expected a list/tuple of str or openclean_pattern.tokenize.token.Token, got: {}".format(value))
            encoded.append(self.resolve_row(tokenized_row=value))
        return encoded

    @abstractmethod
    def resolve_row(self, tokenized_row):
        """returns the atomic / compound data type augmented row. this can be a combination of str
        and openclean_pattern.tokenize.token.Tokens

        Parameters
        ----------
        tokenized_row: tuple[str, openclean_pattern.tokenize.token.Token]
            token to check against the master data

        Returns
        -------
            tuple[openclean_pattern.tokenize.token.Token]
        """
        raise NotImplementedError()

    @abstractmethod
    def get_vocabulary(self):
        """gets the data in used to build the resolver if any

        Returns
        -------
            list or nothing if Atomic
        """
        raise NotImplementedError()


class DefaultTypeResolver(TypeResolver):
    """ The DefaultTypeResolver to be used. The general idea here is to always have the AtomicTypeResolver
    present and attach middleware TypeResolvers to add compound type resolution if needed. The order in which
    they are entered prioritizes between them. e.g. if DataTime takes preference over GeoSpatial, a
    county called March County would be identified as (_MONTH_, _ALPHA_ ) instead of ( _COUNTY_ )
    """

    def __init__(self, interceptors=None):
        """ Initializes the DefaultTypeResolver.
        
        Parameters
        ----------
            interceptors: List[TypeResolver]
                the type resolvers for compound resolution
        """
        if interceptors is None:
            interceptors = []

        if not isinstance(interceptors, list):
            if isinstance(interceptors, TypeResolver):
                interceptors = [interceptors]
            else:
                raise TypeError('expected a TypeResolver or a list of TypeResolvers. Got {}'.format(interceptors))

        interceptors.append(AtomicTypeResolver())
        self.interceptors = interceptors

    def resolve_row(self, tokenized_row):
        """passes through all the middlewares and adding found compound types and finally through the
        AtomicTypeResolver
        """
        for mw in self.interceptors:
            tokenized_row = mw.resolve_row(tokenized_row)
        return tokenized_row

    def get_vocabulary(self):
        """gets the data in used to build the resolver

        Returns
        -------
            nothing
        """
        pass


class AtomicTypeResolver(TypeResolver):
    """ Class to resolve to the supported atomic types
            STRING = STRING_REP = '\W+'
            ALPHA = ALPHA_REP = 'ALPHA'
            ALPHANUM = ALPHANUM_REP = 'ALPHANUM'
            DIGIT = DIGIT_REP = 'NUMERIC'
            PUNCTUATION = PUNCTUATION_REP = 'PUNC'
            GAP = 'G'
            SPACE_REP = '\S'
            OPTIONAL_REP = '?'
    """

    def resolve_row(self, tokenized_row):
        """returns the data type

        Parameters
        ----------
        tokenized_row: tuple[str]
            tokens to check the data types of

        Returns
        -------
            tuple[openclean_pattern.tokenize.token.Token]
        """
        resolved = list()
        for token in tokenized_row:
            # If it isn't already a Token (from some other resolver)
            if not isinstance(token, Token):
                if token.isdigit():
                    type = SupportedDataTypes.DIGIT
                elif token.isalpha():
                    type = SupportedDataTypes.ALPHA
                elif token.isalnum():
                    type = SupportedDataTypes.ALPHANUM
                elif token.isspace():
                    type = SupportedDataTypes.SPACE_REP
                else:
                    type = SupportedDataTypes.PUNCTUATION
                token = Token(regex_type=type, size=len(token), value=token)
            resolved.append(token)

        return tuple(resolved)

    def get_vocabulary(self):
        """gets the data in used to build the resolver

        Returns
        -------
            nothing
        """
        pass


class CompoundTypeResolver(TypeResolver, metaclass=ABCMeta):
    """Compound type resolver. It lookups the prefix tree for a match and then returns the respective label.
    If it fails to find a good compound match for a token, it returns the str token value. The prefix tree exists
    to enhance performance
     """

    def __init__(self, words):
        """initializes the prefix tree

        Parameters
        ---------
        words: list
            list of words for the prefix tree
        """
        self.words = words
        self.pt = PrefixTree(words)

    def resolve_row(self, tokenized_row):
        """idenfifier compound data types in the tokenized_row and replaces them with Tokens.

        Parameters
        ----------
        tokenized_row: tuple[str]
            tokens to check against the master data
        Returns
        -------
            tuple[str, openclean_pattern.tokenize.token.Token]
        """
        prefixes = self.find_prefixes(list(tokenized_row))
        # todo: support ignoring punctuation when extracting prefixes from row
        p = 0
        while p < len(prefixes):
            c = list()
            for ai in tokenized_row:
                if not isinstance(ai, Token):
                    splits = re.split(r'(\b' + prefixes[p] + r'\b)', ai)
                    b = list()
                    for split in splits:
                        if split == prefixes[p]:
                            ctype = self.get_label(split)
                            b.append(Token(regex_type=ctype,
                                           size=len(split),
                                           value=split))
                        elif split != '':
                            b.append(split)
                    c.append(b)
                else:
                    c.append([ai])
            tokenized_row = [item for sublist in c for item in sublist]
            p += 1

        return tuple(tokenized_row)

    def get_vocabulary(self):
        """gets the data used to build the tree

        Returns
        -------
            list
        """
        raise self.words

    def find_prefixes(self, tokenized_row):
        """lookups tokens in prefix tree for matches and sorts the prefixes by descending order in no. of tokens

        Parameters
        ----------
        tokenized_row: list of tokens
            the tokens to search for in the prefix tree
        """
        prefixes = self.pt.prefix_search(list(tokenized_row), ignore_punc=True)
        return sorted(prefixes, key=lambda x: len(x), reverse=True)

    @abstractmethod
    def get_label(self, value):
        """Gets compound type for the detected prefix from the vocabulary.

        Parameters
        ----------
        value: str
            prefix found in the row
        """
        raise NotImplementedError()


class DateResolver(CompoundTypeResolver):
    """Resolves date times"""

    def __init__(self):
        """Initializes the datetime resolver. Preloads data about weekdays and months and builds a prefix tree
        """
        # todo: add pandas datetime inference?
        self.weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Mon', 'Tue',
                         'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']
        self.months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                       'November', 'December',
                       'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Sep', 'Oct', 'Nov', 'Dec']

        self.wd = list()
        [self.wd.append(w.lower()) for w in self.weekdays]
        self.mo = list()
        [self.mo.append(m.lower()) for m in self.months]

        self.words = self.wd + self.mo
        super(DateResolver, self).__init__(self.words)

    def get_label(self, value):
        """Gets compound type for the detected prefix from the master vocabulary.

        Parameters
        ----------
        value: str
            prefix found in the row
        """
        if value in self.wd:
            return SupportedDataTypes.WEEKDAY
        if value in self.mo:
            return SupportedDataTypes.MONTH
        else:
            raise KeyError("{} missing in vocabulary but present in PrefixTree!".format(value))

# todo: geospatial resolver
# class GeoSpatialResolver(CompoundTypeResolver, datamart_geo.GeoData):
#     def __init__(self):
#         areas = list()
#
#         self.gs = datamart_geo.GeoData(os.path.join(os.path.abspath('.'), '../datamart-geo/data'))
#         self.gs.load_areas([0, 1, 2])  # already lowercased
#         [areas.append(area) for area in self.gs._area_names]
#         self.areas = PrefixTree(areas)
#
#     def resolve_row(self, tokenized_row):
#         name = token.lower()
#         if self.gs.resolve_names([name]) != [None]:
#             return self.get_geotype(self.gs.resolve_names([name])[0].level)
#         return False
#
#     def lookup_name(self, name):
#         name = name.lower()
#         if name in self.areas.prefix_search(name):
#             return True
#         return False
#
#     def get_area_trie(self):
#         # returns prefix tree
#         return self.areas
#
#     def get_vocabulary(self):
#         areas = list()
#         self.gs.load_areas([0, 1, 2])  # already lowercased
#         [areas.append(area) for area in self.gs._area_names]
#         return areas
#
#     @staticmethod
#     def get_geotype(level):
#         labels = [SupportedDataTypes.COUNTRY, SupportedDataTypes.STATE, SupportedDataTypes.COUNTY]
#         if level in range(0, len(labels)):
#             return labels[level]
#         else:
#             return None


class BusinessEntityResolver(CompoundTypeResolver):
    """Resolves Business Entity Suffixes"""

    def __init__(self):
        """Initializes the business entity resolver. Preloads data about company suffixes and builds a prefix tree
        """
        # extracted using regex from https://www.harborcompliance.com/information/company-suffixes
        self.words = pd.read_csv(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../resources/data/company_suffixes.csv'),
            squeeze=True).str.replace('.', '').str.lower().tolist()  # replace dots for all abbreviations

        super(BusinessEntityResolver, self).__init__(self.words)

    def get_label(self, value):
        """Gets compound type for the detected prefix from the master vocabulary.

        Parameters
        ----------
        value: str
            prefix found in the row
        """
        if value in self.words:
            return SupportedDataTypes.BE
        else:
            raise KeyError("{} missing in vocabulary but present in PrefixTree!".format(value))


class AddressDesignatorResolver(CompoundTypeResolver):
    """ Resolves street abbreviations and suds"""

    def __init__(self):
        """ initializes address designator resolver by preloading street and sud dat"""
        self.dtype = ''
        # https://pe.usps.com/text/pub28/28apc_002.htm
        street = pd.read_csv(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../resources/data/street_abvs.csv'))
        street = set(street.fillna('').applymap(str.lower).values.flatten())
        street.discard('')
        self.street = list(street)

        # https://pe.usps.com/text/pub28/28apc_003.htm
        sud = pd.read_csv(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../resources/data/secondary_unit_designtor.csv'))
        sud = set(sud.fillna('').applymap(str.lower).values.flatten())
        sud.discard('')
        self.sud = list(sud)

        self.words = self.street + self.sud
        super(AddressDesignatorResolver, self).__init__(self.words)

    def get_label(self, value):
        """Gets compound type for the detected prefix from the master vocabulary.

        Parameters
        ----------
        value: str
            prefix found in the row
        """
        if value in self.street:
            return SupportedDataTypes.STREET
        if value in self.sud:
            return SupportedDataTypes.SUD
        else:
            raise KeyError("{} missing in vocabulary but present in PrefixTree!".format(value))
