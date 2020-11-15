# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.datatypes.resolver import DateResolver, DefaultTypeResolver, AtomicTypeResolver
from openclean_pattern.tokenize.regex import RegexTokenizer


"""unit tests for geospatial resolvers"""

import pytest


def test_geospatial_resolver(dates):
    pass