====================================================
openclean-pattern - openclean Pattern Identification
====================================================

.. image:: https://img.shields.io/badge/License-BSD-green.svg
    :target: https://github.com/VIDA-NYU/openclean-pattern/blob/master/LICENSE


.. figure:: https://github.com/VIDA-NYU/openclean-pattern/blob/master/docs/graphics/logo.png
    :align: center
    :alt: openclean Logo


About
=====
This package identifies patterns and creates Openclean Patterns from data. It is part of the openclean-core library to create profiled results as well as to detect anomalies.
Currently, Openclean Patterns support the following data types, but are fairly extensible to any other basic / nonbasic implementations:

- Basic
    - String
    - Integers
    - Punctuations
    - Spaces

- Non-Basic/Advanced
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
=======
The library comes with many predefined classes to support the pattern detection process. One could use the `OpencleanPatternFinder <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/opencleanpatternfinder.py#L29>`_ class or otherwise the general process should look similar to the following:

#. Sample the column
    In case of very large dataset two Samplers have been added for the user's convenience to help extract the distribution of the column:
     - `RandomSampler <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/utils/utils.py#L236>`_: considers each item in the iterable equally probable to get selected
     - `WeightedRandomSampler <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/utils/utils.py#L161>`_: takes a Counter of type {value:frequency} and creates a sample using the Counter distribution.
     - `Distinct <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/utils/utils.py#L161>`_: selects only distinct rows

#. Tokenize it to remove punctutation
    At this point TypeResolvers can also be injected to tokenize and encode in the same run instead of running it as a separate step 3:
     - `RegexTokenizer <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/tokenize/regex.py#L16>`_: tokenizes using the default regex that breaks the row values into a list of tokens keeping the delimiters intact (unless a user provides a custom regex). It also changes the tokens to lower case letters. The user also has the option to define if they want to consider e.g. the string 'a.b.c' as delimited by the '.' character or consider it as an abbreviation character and keep 'abc' intact.
     - `DefaultTokenizer <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/tokenize/regex.py#L97>`_ Follows the Regex Tokenizer process and the uses the DefaultTypeResolver to resolve token types.

#. Resolve Types
    This stage converts the tokens to their `Basic and Non-Basic representations <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/datatypes/base.py#L13>`_:
     - `BasicTypeResolver <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/datatypes/resolver.py#L117>`_: converts the row into the above mentioned BasicTypes.
     - `AdvancedTypeResolver <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/datatypes/resolver.py#L172>`_: has numerous implementations and can be easily extended to add new AdvancedTypeResolver classes.
        - DateResolver
        - BusinessEntityResolver
        - AddressDesignatorResolver
        - GeoSpatialResolver
     - `DefaultTypeResolver <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/datatypes/resolver.py#L72>`_: does both Basic and Non-Basic type resolution by letting a user add Non-Basic interceptors before the Basic type resolution operation.

#. Collect and/or Align
    Create groups of similar rows and align them:
     - `Cluster <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/align/cluster.py#L21>`_: Collect similar tokenized rows by either clustering them using DBSCAN choosing a precomputed `distance <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/align/distance/base.py#L13>`_.
     - `Group <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/align/group.py#L17>`_: Grouping tokenized rows with similar lengths
     - `CombAlign <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/align/combinatorics.py#L31>`_ [#]_: looks at all the possible combinations of each token in each row with other all other rows, calculates the distance, clusters the closest alignments together using DBSCAN and returns the clustered groups.

#. Compile a pattern
    Generate a regex pattern from the aligned groups:
     - `DefaultRegexCompiler <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/openclean_pattern/regex/base.py#L14>`_ : Analyzes each token position and the different datatypes that appear at that position iterating through each row. Then selects the majority type as the pattern at that position. Combining positional regex's compiles a full expression for the column.
        - ``method=col``: Compiles the pattern based on the positions of different tokens at in each row. It flags values that don't match the specific position's majority types as anomalies.
        - ``method=row``: Compiles the pattern using each full row as a possible pattern.


.. [#] Not recommended for large datasets or cases where the number of combinations between rows is too large (e.g. one row has 16 tokens and other has 6, the total no. of distance computation just for this combination would be 16P6 =  5765760) - to be updated to using majority pooling alignment / minimum set cover.

Upcoming Modules
================
- serializer / deserializer
- multiple sequence alignment


Examples
========
We include several `notebooks <https://github.com/maqzi/openclean/blob/9c6d938c19f076435efaae4d705ec92a8f1f00bd/examples/>`_ in this repository that demonstrate **openclean-pattern**'s usage.


See also:
=========

* `openclean-core <https://github.com/VIDA-NYU/openclean-core>`__
* `openclean-notebook <https://github.com/VIDA-NYU/openclean-notebook>`__
* `Datamart-Geo <https://gitlab.com/ViDA-NYU/datamart/datamart-geo>`__
