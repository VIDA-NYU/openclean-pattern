# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Supported Data types and their string representations"""

import enum


class SupportedDataTypes(enum.Enum):
    """
    Enum class for all supported datatypes and their representations
    """
    # ATOMIC TYPES
    STRING = STRING_REP = '\W+'
    ALPHA = ALPHA_REP = 'ALPHA'
    ALPHANUM = ALPHANUM_REP = 'ALPHANUM'
    DIGIT = DIGIT_REP = 'NUMERIC'
    PUNCTUATION = PUNCTUATION_REP = 'PUNC'
    GAP = 'G'
    SPACE_REP = '\S'
    OPTIONAL_REP = '?'

    # SUPPORTED COMPOUND TYPES
    MONTH = 'MONTH'
    WEEKDAY = 'WEEKDAY'
    DATETIME = 'DATETIME'
    STATE = 'STATE'
    COUNTRY = 'COUNTRY'
    COUNTY = 'COUNTY'
    BE = 'BUSINESS'
    STREET = 'STREET'
    SUD = 'SUD' #SECONDARY_UNIT_DESIGNATOR