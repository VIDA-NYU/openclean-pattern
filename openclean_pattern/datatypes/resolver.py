# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Classes responsible for resolving various compound data types"""

import pandas as pd, os, datamart_geo

from openclean_pattern.tokenize.prefix_tree import PrefixTree
from openclean_pattern.datatypes.base import SupportedDataTypes

from abc import abstractmethod, ABCMeta


class DataTypeResolver(metaclass=ABCMeta):
    """A compound data type resolver object """

    @abstractmethod
    def resolve(self, token):
        """returns a compound data type

        Parameters
        ----------
        token: str
            token to check against the master data

        Returns
        -------
            SupportedDataTypes.enum
        """
        raise NotImplementedError()

    @abstractmethod
    def get_vocabulary(self):
        """gets the data in used to build the resolver

        Returns
        -------
            list
        """
        raise NotImplementedError()


class DefaultTypeResolver(DataTypeResolver):
    """Default type resolver. Returns the first type identified in the following order:
        1. DateTime
        2. GeoSpatial
        3. BusinessEntity
        4. AddressDesignator
     """

    def __init__(self):
        """Initializes the resolvers"""
        self.dt = DateTimeResolver()
        self.gs = GeoSpatialResolver()
        self.be = BusinessEntityResolver()
        self.ad = AddressDesignatorResolver()

    def resolve(self, token):
        """returns a compound data type

        Parameters
        ----------
        token: str
            token to check against the master data
        Returns
        -------
            SupportedDataTypes.enum
        """
        dtr = self.dt.resolve(token=token)
        if dtr:
            return dtr
        else:
            gsr = self.gs.resolve(token=token)
            if gsr:
                return gsr
            else:
                ber = self.be.resolve(token=token)
                if ber:
                    return ber
                else:
                    adr = self.ad.resolve(token=token)
                    if adr:
                        return adr
                    else:
                        return token

    def get_vocabulary(self):
        """gets the data in used to build the resolver

        Returns
        -------
            list
        """
        raise NotImplementedError()


class DateTimeResolver(DataTypeResolver):
    """Resolves date times"""

    def __init__(self):
        """Initializes the datetime resolver. Preloads data about weekdays and months and builds a prefix tree
        """
        self.weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Mon', 'Tue',
                         'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']
        self.months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                       'November', 'December',
                       'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Sep', 'Oct', 'Nov', 'Dec']

        self.wd = list()
        [self.wd.append(w.lower()) for w in self.weekdays]
        self.mo = list()
        [self.mo.append(m.lower()) for m in self.months]
        self.dates = PrefixTree(self.wd + self.mo)

    def resolve(self, token):
        # todo: add pandas datetime inference?
        if token.lower() in self.wd:
            return SupportedDataTypes.WEEKDAY
        if token.lower() in self.mo:
            return SupportedDataTypes.MONTH
        return False

    def get_vocabulary(self):
        x = list()
        [x.append(l.lower()) for l in self.weekdays + self.months]
        return x

    def find_prefixes(self, content):
        return self.dates.prefix_search(content.lower())


class GeoSpatialResolver(DataTypeResolver, datamart_geo.GeoData):
    def __init__(self):
        areas = list()
        # todo: config file?
        self.gs = datamart_geo.GeoData(os.path.join(os.path.abspath('.'), '../datamart-geo/data'))
        self.gs.load_areas([0, 1, 2])  # already lowercased
        [areas.append(area) for area in self.gs._area_names]
        self.areas = PrefixTree(areas)

    def resolve(self, token):
        name = token.lower()
        if self.gs.resolve_names([name]) != [None]:
            return self.get_geotype(self.gs.resolve_names([name])[0].level)
        return False

    def lookup_name(self, name):
        name = name.lower()
        if name in self.areas.prefix_search(name):
            return True
        return False

    def find_prefixes(self, content):
        return self.areas.prefix_search(content.lower())

    def get_area_trie(self):
        # returns prefix tree
        return self.areas

    def get_vocabulary(self):
        areas = list()
        self.gs.load_areas([0, 1, 2])  # already lowercased
        [areas.append(area) for area in self.gs._area_names]
        return areas

    @staticmethod
    def get_geotype(level):
        labels = [SupportedDataTypes.COUNTRY, SupportedDataTypes.STATE, SupportedDataTypes.COUNTY]
        if level in range(0, len(labels)):
            return labels[level]
        else:
            return None


class BusinessEntityResolver(DataTypeResolver):
    def __init__(self):
        # extracted using regex from https://www.harborcompliance.com/information/company-suffixes
        self.be = pd.read_csv(
            os.path.join(os.path.abspath('.'), 'resources/company_suffixes.csv'),
            squeeze=True).str.lower().tolist()
        self.bes = PrefixTree(self.be)

    def resolve(self, token):
        name = token.lower()
        if name in self.be:
            return SupportedDataTypes.BE
        return False

    def get_vocabulary(self):
        x = list()
        [x.append(l.lower()) for l in self.be]
        return x

    def find_prefixes(self, content):
        return self.bes.prefix_search(content.lower(), abbreviations=True)


class AddressDesignatorResolver(DataTypeResolver):
    def __init__(self):
        self.dtype = ''
        # https://pe.usps.com/text/pub28/28apc_002.htm
        street = pd.read_csv(
            os.path.join(os.path.abspath('.'), 'resources/street_abvs.csv'))
        street = set(street.fillna('').applymap(str.lower).values.flatten())
        street.discard('')
        self.street = street

        # https://pe.usps.com/text/pub28/28apc_003.htm
        sud = pd.read_csv(os.path.join(
            os.path.abspath('.'), 'resources/secondary_unit_designtor.csv'))
        sud = set(sud.fillna('').applymap(str.lower).values.flatten())
        sud.discard('')
        self.sud = sud

        self.ads = PrefixTree(list(self.street) + list(self.sud))

    def resolve(self, token):
        name = token.lower()
        if name in self.street:
            return SupportedDataTypes.STREET
        elif name in self.sud:
            return SupportedDataTypes.SUD
        return False

    def get_vocabulary(self):
        x = list()
        [x.append(l.lower()) for l in list(self.street) + list(self.sud)]
        return x

    def find_prefixes(self, content):
        return self.ads.prefix_search(content.lower())
