# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.


import os
import pandas as pd
import pytest


DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.files')
BUSINESS = os.path.join(DIR, 'business.csv')


@pytest.fixture
def dates():
    """Get a simple series with dates"""
    data = [
        ['Monday, 21st March, 2019'],
        ['Wed, October 19, 1990'],
        ['Sun Jan 2010'],
        ['Dec 3']
    ]
    return pd.Series(data=data)


@pytest.fixture
def business():
    """Load the business dataset"""
    return pd.read_csv(BUSINESS)

