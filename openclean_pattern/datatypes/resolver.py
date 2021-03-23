# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Classes responsible for resolving various non-basic and basic data types into Tokens.
"""

import pandas as pd, os, datamart_geo, re
import sqlite3

from openclean_pattern.tokenize.prefix_tree import PrefixTree
from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.tokenize.token import Token

from abc import abstractmethod, ABCMeta

RESOURCES = '../../resources/data/'


class TypeResolver(metaclass=ABCMeta):
    """This class resolves different data types"""

    def resolve(self, column, tokenizer=None):
        """resolves the rows in the column into their type representations

        Parameters
        ----------
        column: list of lists/tuples of [str, openclean_pattern.tokenize.token.Tokens]
            list of column values
        tokenizer: openclean_pattern.tokenize.base.Tokenizer
            Tokenizer to use as part of the encoding

        Returns
        -------
        list of tupled tokens
        """
        if tokenizer is None:
            from openclean_pattern.tokenize.regex import RegexTokenizer
            tokenizer = RegexTokenizer(type_resolver=self)
        else:
            tokenizer.type_resolver = self

        encoded = tokenizer.encode(column)
        return encoded

    @abstractmethod
    def resolve_row(self, rowidx, row, tokenizer):
        """returns the basic / non-basic data type augmented row. this can be a combination of str
        and openclean_pattern.tokenize.token.Tokens

        Parameters
        ----------
        rowidx: int
            row id
        row: str/tuple[str]
            row to tokenize and resolve tokens against the masterdata
        tokenizer: callable (Tokenizer.tokenize)
            tokenizes the string row

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
            list or nothing if basic
        """
        raise NotImplementedError()

    @staticmethod
    def gap(rowidx):
        """returns a gap Token

        Parameters
        ----------
        rowidx: int
            row id

        Returns
        -------
            Token
        """
        return Token(regex_type=SupportedDataTypes.GAP, value='', rowidx=rowidx)


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

    def resolve_row(self, rowidx, row, tokenizer):
        """passes through all the middlewares and adding found non-basic types and finally through the
        BasicTypeResolver
        """
        for mw in self.interceptors:
            row = mw.resolve_row(rowidx, row, tokenizer)
        return row

    def get_vocabulary(self):
        """gets the data in used to build the resolver

        Returns
        -------
            nothing
        """
        pass


class BasicTypeResolver(TypeResolver):
    """ Class to resolve to the supported basic types
            STRING = STRING_REP = '\W+'
            ALPHA = ALPHA_REP = 'ALPHA'
            ALPHANUM = ALPHANUM_REP = 'ALPHANUM'
            DIGIT = DIGIT_REP = 'NUMERIC'
            PUNCTUATION = PUNCTUATION_REP = 'PUNC'
            GAP = 'G'
            SPACE_REP = '\S'
            OPTIONAL_REP = '?'
    """

    def resolve_row(self, rowidx, row, tokenizer):
        """returns the data type

        Parameters
        ----------
        rowidx: int
            row id
        row: tuple[str]
            row to tokenize and resolve tokens against the masterdata
        tokenizer: callable (Tokenizer.tokenize)
            tokenizes the string row

        Returns
        -------
            tuple[openclean_pattern.tokenize.token.Token]
        """
        if isinstance(row, str):
            row = [row]

        resolved = list()
        for element in row:
            # If it isn't already a Token (from some other resolver)
            if not isinstance(element, Token):
                if isinstance(element, str):
                    tokenized_row = tokenizer(rowidx, element)
                else:
                    raise ValueError("invalid token type. Acceptable types: str or {}".format(Token.__class__))

                for token in tokenized_row:
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
                    token = Token(regex_type=type, value=token, rowidx=rowidx)
                    resolved.append(token)
            else:
                resolved.append(element)

        return tuple(resolved)

    def get_vocabulary(self):
        """gets the data in used to build the resolver

        Returns
        -------
            nothing
        """
        pass


class AdvancedTypeResolver(TypeResolver, metaclass=ABCMeta):
    """Non-basic type resolver. It lookups the prefix tree for a match and then returns the respective label.
    If it fails to find a good non-basic match for a token, it returns the str token value. The prefix tree exists
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

    def resolve_row(self, rowidx, row, tokenizer):
        """idenfifier non-basic data types in the tokenized_row and replaces them with Tokens.

        Parameters
        ----------
        rowidx: int
            row id
        row: tuple[str]
            row to tokenize and resolve tokens against the masterdata
        tokenizer: callable (Tokenizer.tokenize)
            tokenizes the string row parts

        Returns
        -------
            tuple[str, openclean_pattern.tokenize.token.Token]
        """
        # todo: support ignoring punctuation when extracting prefixes from row
        # convert string to list
        if isinstance(row, str):
            row = [row]

        # if list is e.g. [str, Tok, str]
        prefixes = list()
        for element in row:
            if isinstance(element, str):
                tokenized_element = tokenizer(rowidx, element)
                pxs = self.find_prefixes(list(tokenized_element))
                for px in pxs:
                    prefixes.append(px)

        # sort prefixes by length
        prefixes = sorted(prefixes, key=lambda x: len(x), reverse=True)

        # go through the elements and replace str elements with tokens from found prefixes
        p = 0
        while p < len(prefixes):
            prefix_processed_row = list()
            for element in row:
                if not isinstance(element, Token):
                    prefix = prefixes[p]
                    splits = re.split(r'(\b' + prefix + r'\b)', element)
                    split_row = list()
                    for split in splits:
                        if split == prefix:
                            ctype = self.get_label(split)
                            split_row.append(Token(regex_type=ctype,
                                                   value=split,
                                                   rowidx=rowidx))
                        elif split != '':
                            split_row.append(split)
                    prefix_processed_row.append(split_row)
                else:
                    prefix_processed_row.append([element])
            row = [item for sublist in prefix_processed_row for item in sublist]
            p += 1

        return tuple(row)

    def get_vocabulary(self):
        """gets the data used to build the tree

        Returns
        -------
            list
        """
        return self.words

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
        """Gets non-basic type for the detected prefix from the vocabulary.

        Parameters
        ----------
        value: str
            prefix found in the row
        """
        raise NotImplementedError()


class DateResolver(AdvancedTypeResolver):
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
        """Gets non-basic type for the detected prefix from the master vocabulary.

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


class GeoSpatialResolver(AdvancedTypeResolver):
    """Resolves geo spatial types"""

    def __init__(self, levels=None):
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
        GEOPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), RESOURCES)
        datamart_geo.GeoData.download(GEOPATH, update=False)

        # Read sqlite query results into a pandas DataFrame
        con = sqlite3.connect(os.path.join(GEOPATH, 'admins.sqlite3'))
        geodata = pd.read_sql_query("SELECT name, level from admins", con)

        self.admins = list()
        for level in levels:
            self.admins.append(geodata[geodata['level'] == level]['name'].str.lower().to_list())

        # Convert dataframe into prefix tree
        self.areas = list()
        for admin in self.admins:
            self.areas += admin

        # todo: pickle full tree?

        super(GeoSpatialResolver, self).__init__(self.areas)

    def get_label(self, value):
        labels = [SupportedDataTypes.ADMIN_LEVEL_0,
                  SupportedDataTypes.ADMIN_LEVEL_1,
                  SupportedDataTypes.ADMIN_LEVEL_2,
                  SupportedDataTypes.ADMIN_LEVEL_3,
                  SupportedDataTypes.ADMIN_LEVEL_4,
                  SupportedDataTypes.ADMIN_LEVEL_5]

        for i, admin in enumerate(self.admins):
            if value in admin:
                return labels[i]

        raise KeyError("{} missing in vocabulary but present in PrefixTree!".format(value))


class BusinessEntityResolver(AdvancedTypeResolver):
    """Resolves Business Entity Suffixes"""

    def __init__(self):
        """Initializes the business entity resolver. Preloads data about company suffixes and builds a prefix tree
        """
        # extracted using regex from https://www.harborcompliance.com/information/company-suffixes
        self.words = pd.read_csv(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), RESOURCES, 'company_suffixes.csv'),
            squeeze=True).str.replace('.', '').str.lower().tolist()  # replace dots for all abbreviations

        super(BusinessEntityResolver, self).__init__(self.words)

    def get_label(self, value):
        """Gets non-basic type for the detected prefix from the master vocabulary.

        Parameters
        ----------
        value: str
            prefix found in the row
        """
        if value in self.words:
            return SupportedDataTypes.BE
        else:
            raise KeyError("{} missing in vocabulary but present in PrefixTree!".format(value))


class AddressDesignatorResolver(AdvancedTypeResolver):
    """ Resolves street abbreviations and suds"""

    def __init__(self):
        """ initializes address designator resolver by preloading street and sud dat"""
        self.dtype = ''
        # https://pe.usps.com/text/pub28/28apc_002.htm
        street = pd.read_csv(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), RESOURCES, 'street_abvs.csv'))
        street = set(street.fillna('').applymap(str.lower).values.flatten())
        street.discard('')
        self.street = list(street)

        # https://pe.usps.com/text/pub28/28apc_003.htm
        sud = pd.read_csv(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), RESOURCES, 'secondary_unit_designtor.csv'))
        sud = set(sud.fillna('').applymap(str.lower).values.flatten())
        sud.discard('')
        self.sud = list(sud)

        self.words = self.street + self.sud
        super(AddressDesignatorResolver, self).__init__(self.words)

    def get_label(self, value):
        """Gets non-basic type for the detected prefix from the master vocabulary.

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
