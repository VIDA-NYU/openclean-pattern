# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Required packages for install, test, docs, and tests."""


import os
import re

from setuptools import setup, find_packages

install_requires = [
    'pandas',
    'numpy',
    'datamart_geo>=0.2.1',
    'pygtrie==2.3.3',
    'scikit-bio',
    'openclean-core>=0.3.0'
]

tests_require = [
    'coverage>=5.0',
    'pytest',
    'pytest-cov'
]


dev_require = ['flake8'] + tests_require


extras_require = {
    'docs': [
        'Sphinx',
        'sphinx-rtd-theme'
    ],
    'tests': tests_require,
    'dev': dev_require
}


# Get the version string from the version.py file in the openclean-patternpackage.
with open(os.path.join('openclean_pattern', 'version.py'), 'rt') as f:
    filecontent = f.read()
match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", filecontent, re.M)
if match is not None:
    version = match.group(1)
else:
    raise RuntimeError('unable to find version string in %s.' % (filecontent,))


# Get long project description text from the README.rst file
with open('README.rst', 'rt') as f:
    description = f.read()


# todo: update urls
setup(
    name='openclean_pattern',
    version=version,
    description="Library for pattern and anomalous pattern detection",
    long_description=description,
    long_description_content_type='text/x-rst',
    keywords=['openclean_pattern', 'pattern detection'],
    url='https://github.com/VIDA-NYU/openclean-pattern',
    author='Munaf Qazi',
    author_email='munaf.qazi@gmail.com',
    license='New BSD',
    license_file='LICENSE',
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    extras_require=extras_require,
    tests_require=tests_require,
    install_requires=install_requires,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python'
    ]
)
