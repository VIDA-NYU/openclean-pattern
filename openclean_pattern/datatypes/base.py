# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Supported Data types and their string representations"""

import openclean.function.token.base as TT


def create_gap_token(rowidx=None):
    """returns a gap Token

    Parameters
    ----------
    rowidx: int (Optional)
        row id

    Returns
    -------
    Token
    """
    return TT.Token(token_type=SupportedDataTypes.GAP, value='', rowidx=rowidx)


class SupportedDataTypes:
    """
    Enum class for all supported datatypes and their representations
    """
    # BASIC TYPES
    STRING = STRING_REP = '\\W+'
    ALPHA = ALPHA_REP = TT.ALPHA
    ALPHANUM = ALPHANUM_REP = TT.ALPHANUM
    DIGIT = DIGIT_REP = TT.DIGIT
    PUNCTUATION = PUNCTUATION_REP = TT.PUNCTUATION
    GAP = 'GAP'  # ALIGNMENT GAP CHARACTER
    SPACE_REP = '\\S'
    OPTIONAL_REP = '?'  # POST REGEX OPTIONAL CHARACTER

    # SUPPORTED NONBASIC TYPES
    MONTH = 'MONTH'
    WEEKDAY = 'WEEKDAY'
    DATETIME = 'DATETIME'
    STATE = 'STATE'
    COUNTRY = 'COUNTRY'
    COUNTY = 'COUNTY'
    BE = 'BUSINESS'
    STREET = 'STREET'
    SUD = 'SUD'  # SECONDARY_UNIT_DESIGNATOR

    # DATAMART_GEO TYPES
    ADMIN_LEVEL_0 = 'ADMIN_0'
    ADMIN_LEVEL_1 = 'ADMIN_1'
    ADMIN_LEVEL_2 = 'ADMIN_2'
    ADMIN_LEVEL_3 = 'ADMIN_3'
    ADMIN_LEVEL_4 = 'ADMIN_4'
    ADMIN_LEVEL_5 = 'ADMIN_5'
