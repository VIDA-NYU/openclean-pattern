# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.


import os
import pandas as pd
import pytest
from openclean.pipeline import stream

DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.files')
BUSINESS = os.path.join(DIR, 'business.csv')
CHECKINTIME = os.path.join(DIR, 'check-in-time.txt.gz')
YEAR = os.path.join(DIR, 'year.txt.gz')
SPECIMEN = os.path.join(DIR, 'specimen.txt.gz')
URBAN = os.path.join(DIR, 'urban.csv')


@pytest.fixture
def dates():
    """Get a simple series with dates"""
    data = [
        'Monday, 21st March, 2019',
        'Wed, October 19, 1990',
        'Sun Jan 2010',
        'Dec 3'
    ]
    return pd.Series(data=data)


@pytest.fixture
def business():
    """Load the business dataset"""
    return pd.read_csv(BUSINESS)


@pytest.fixture
def checkintime():
    """Load the check in time dataset"""
    return stream(CHECKINTIME, header=['term', 'freq'], delim='\t', compressed=True)\
        .select('term')\
        .sample(1000, random_state=42)\
        .to_df()['term']


@pytest.fixture
def specimen():
    """Load the specimen dataset"""
    return stream(SPECIMEN, header=['term', 'freq'], delim='\t', compressed=True)\
        .select('term')\
        .sample(1000, random_state=42)\
        .to_df()['term']


@pytest.fixture
def year():
    """Load the year dataset"""
    return stream(YEAR, header=['term', 'freq'], delim='\t', compressed=True)\
        .select('term')\
        .sample(1000, random_state=42)\
        .to_df()['term']

@pytest.fixture
def urban():
    """Load the urban dataset"""
    test_data = stream(URBAN)\
        .select(['Address ', 'Address Continued', 'City', 'State', 'Zip Code'])\
        .to_df()

    geo = test_data[['Address ', 'Address Continued', 'City', 'State', 'Zip Code']]
    geo.loc[:, 'Full Address'] = test_data['Address '] + ',\n' + test_data['Address Continued'].fillna('') + '\n' + \
                                 test_data['City'] + ', ' + test_data['State'] + ', ' + test_data['Zip Code']
    return geo['Full Address'].to_list()