==========================================
openclean-pattern - Pattern Identification
==========================================

.. image:: https://img.shields.io/badge/License-BSD-green.svg
    :target: https://github.com/maqzi/openclean/blob/master/LICENSE


About
=====
This package identifies regex patterns in data with the option of sequence aligning input values first. It supports the following data types:

- Atomic
    - String
    - Integers
    - Punctuations
    - Spaces

- Compound
    - Dates
        - days of the week and months
    - Business Entities
        - using corporation suffixes
    - Geospatial Entities
        - using datamart-geo for administrative levels (in progress)
    - Address
        - USPS street abreviations and secondary unit designators for addresses

The package has been extended to identify anomalous patterns inside the data as well.


Installation
============
Install **openclean-pattern** from the  `Python Package Index (PyPI) <https://pypi.org/>`_ using ``pip`` with:

.. code-block:: bash

    pip install openclean-pattern

Usage
=====
The library comes with many predefined classes to support the pattern detection process. One could use the `PatternFinder <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/patternfinder.py#L29>`_ class or otherwise the general process should look similar to the following:

#. Sample the column
    In case of very large dataset two Samplers have been added for the user's convenience to help extract the distribution of the column:
     - `RandomSampler <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/utils/utils.py#L236>`_: considers each item in the iterable equally probable to get selected
     - `WeightedRandomSampler <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/utils/utils.py#L161>`_: takes a Counter of type {value:frequency} and creates a sample using the Counter distribution.

#. Tokenize it to remove punctutation
    At this point TypeResolvers can also be injected to tokenize and encode in the same run instead of running it as a separate step 3:
     - `RegexTokenizer <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/tokenize/regex.py#L16>`_: tokenizes using the default regex that breaks the row values into a list of tokens keeping the delimiters intact (unless a user provides a custom regex). It also changes the tokens to lower case letters. The user also has the option to define if they want to consider e.g. the string 'a.b.c' as delimited by the '.' character or consider it as an abbreviation character and keep 'abc' intact.
     - `DefaultTokenizer <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/tokenize/regex.py#L97>`_ Follows the Regex Tokenizer process and the uses the DefaultTypeResolver to resolve token types.

#. Resolve Types
    This stage converts the tokens to their `Atomic and Compound representations <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/datatypes/base.py#L13>`_:
     - `AtomicTypeResolver <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/datatypes/resolver.py#L117>`_: converts the row into the above mentioned AtomicTypes.
     - `CompoundTypeResolver <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/datatypes/resolver.py#L172>`_: has numerous implementations and can be easily extended to add new CompoundTypes classes.
      - DateResolver
      - BusinessEntityResolver
      - AddressDesignatorResolver
      - GeoSpatialResolver
     - `DefaultTypeResolver <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/datatypes/resolver.py#L72>`_: does both Atomic and Compound type resolution by letting a user add compound interceptors before the atomic type resolution operation.

#. Align or group
    Group tokenized rows with similar lengths or perform a multiple seqeunce alignment to align all rows:
     - `GroupAlign <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/align/group.py#L17>`_
     - `CombAlign <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/align/combinatorics.py#L31>`_ [#]_: looks at all the possible combinations of each token in each row with other all other rows, calculates the distance, clusters the closest alignments together using DBSCAN and returns the clustered groups.

#. Compile a pattern
    Generate a regex pattern from the aligned groups
     - `DefaultRegexCompiler <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/regex/base.py#L14>`_ : Analyzes each token position and the different datatypes that appear at that position iterating through each row . Then selects the majority type as the pattern at that position. Combining positional regex's compiles a full expression for the column.


.. [#] Not recommended for large datasets or cases where the number of combinations between rows is too large (e.g. one row has 16 tokens and other has 6, the total no. of distance computation just for this combination would be 16P6 =  5765760) - to be updated to using majority pooling alignment / minimum set cover.

Upcoming Modules
================
- integration with datamart_geo for a GeospatialTypeResolver
- ability to evaluate a regex on other columns
- serializer / deserializer
- anomalous pattern detection
- multiple sequence alignment


Examples
========
We include several example notebooks in this repository that demonstrate possible use cases for **openclean-pattern**.


See also:
=========

* `OpenClean <https://github.com/VIDA-NYU/openclean-core>`__
* `OpenClean-Notebook <https://github.com/VIDA-NYU/openclean-notebook>`__
* `Datamart-Geo <https://gitlab.com/ViDA-NYU/datamart/datamart-geo>`__
