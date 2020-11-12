import pandas as pd, json, numpy as np, os, datamart_geo

from openclean.tokenize.prefix_tree import PrefixTree
from openclean.regex import WEEKDAY, MONTH, DATETIME, STATE, COUNTRY, COUNTY, BE, STREET, SUD

class DateTime(object):
    def __init__(self):
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

    def get_label(self, token):
        # todo: add pandas datetime inference?
        if token.lower() in self.wd:
            return WEEKDAY
        if token.lower() in self.mo:
            return MONTH
        return False

    def get_lists(self):
        x = list()
        [x.append(l.lower()) for l in self.weekdays + self.months]
        return x

    def find_prefixes(self, content):
        return self.dates.prefix_search(content.lower())


class GeoSpatial(datamart_geo.GeoData):
    def __init__(self):
        areas = list()
        # todo: config file?
        self.gs = datamart_geo.GeoData(os.path.join(os.path.abspath('.'), '../datamart-geo/data'))
        self.gs.load_areas([0, 1, 2])  # already lowercased
        [areas.append(area) for area in self.gs._area_names]
        self.areas = PrefixTree(areas)

    def get_label(self, name):
        name = name.lower()
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

    @staticmethod
    def get_geotype(level):
        labels = [COUNTRY, STATE, COUNTY]
        if level in range(0, len(labels)):
            return labels[level]
        else:
            return None

class BusinessEntity(object):
    def __init__(self):
        # extracted using regex from https://www.harborcompliance.com/information/company-suffixes
        self.be = pd.read_csv(
            os.path.join(os.path.abspath('.'), 'resources/company_suffixes.csv'),
            squeeze=True).str.lower().tolist()
        self.bes = PrefixTree(self.be)

    def get_label(self, name):
        name = name.lower()
        if name in self.be:
            return BE
        return False

    def get_lists(self):
        x = list()
        [x.append(l.lower()) for l in self.be]
        return x

    def find_prefixes(self, content):
        return self.bes.prefix_search(content.lower(), abbreviations=True)

class AddressDesignator(object):
    def __init__(self):
        self.dtype = ''
        # https://pe.usps.com/text/pub28/28apc_002.htm
        street = pd.read_csv(
            os.path.join(os.path.abspath('.'),'resources/street_abvs.csv'))
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

    def get_label(self, name):
        name = name.lower()
        if name in self.street:
            return STREET
        elif name in self.sud:
            return SUD
        return False

    def get_lists(self):
        x = list()
        [x.append(l.lower()) for l in list(self.street) + list(self.sud)]
        return x

    def find_prefixes(self, content):
        return self.ads.prefix_search(content.lower())
