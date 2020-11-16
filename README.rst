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
The library comes with many predefined classes to support the pattern detection process. One could use the `PatternFinder` class or otherwise the general process should look similar to the following:

1. Sample the column. In case of very large dataset two Samplers have been added for the user's convenience to help extract the distribution of the column:
    - RandomSampler: considers each item in the iterable equally probable to get selected
    - WeightedRandomSampler: takes a Counter of type {value:frequency} and creates a sample using the Counter distribution.
2. Tokenize it to remove punctutation. At this point TypeResolvers can also be injected to tokenize and encode in the same run instead of running it as a separate step 3:
    - Regex Tokenizer: tokenizes using the default regex that breaks the row values into a list of tokens keeping the delimiters intact (unless a user provides a custom regex). It also changes the tokens to lower case letters. The user also has the option to define if they want to consider e.g. the string 'a.b.c' as delimited by the '.' character or consider it as an abbreviation character and keep 'abc' intact.
    - Default Tokenizer Follows the Regex Tokenizer process and the uses the DefaultTypeResolver to resolve token types.
3. Resolve Types. This stage converts the tokens to their Atomic and Compound representations:
    - AtomicTypeResolver: converts the row into the above mentioned AtomicTypes.
    - CompoundTypeResolver: has numerous implementations and new CompoundTypes can easily be added via the `openclean_pattern.datatypes.resolver.CompoundTypeResolver` class.
        - DateResolver
        - BusinessEntityResolver
        - AddressDesignatorResolver
        - GeoSpatialResolver
    - DefaultTypeResolver: does both Atomic and Compound type resolution by letting a user add compound interceptors before the atomic type resolution operation.
4.  Alignment or grouping: group rows with similar lengths or perform a multiple seqeunce alignment by looking at possible token order combinations to align all rows:
        - GroupAlign
        - CombAlign* : looks at all the possible combinations of each token in each row with other all other rows, calculates the distance, clusters the closest alignments together using DBSCAN and returns the clustered groups.
5. Compile a pattern.
    -


* Not recommended for large datasets or cases where the number of combinations between rows is too large (e.g. one row has 16 tokens and other has 6, the total no. of distance computation just for this combination would be 16P6 =  5765760)

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
