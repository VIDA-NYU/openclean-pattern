==========================================
openclean-pattern - Pattern Identification
==========================================

.. image:: https://img.shields.io/badge/License-BSD-green.svg
    :target: https://github.com/heikomuller/histore/blob/master/LICENSE


About
=====
This package identifies regex patterns in data with the option of sequence aligning input values first. It supports the following data types:

- Atomic
    - String
    - Integers

- Compound
    - Dates
    - Business Entities
        - using corporation suffixes
    - Geospatial Entities
        - using datamart-geo for administrative levels
        - USPS street abreviations and secondary unit designators for addresses

The package has been extended to identify anomalous patterns inside the data as well.


Installation
============
Install **openclean-pattern** from the  `Python Package Index (PyPI) <https://pypi.org/>`_ using ``pip`` with:

.. code-block:: bash

    pip install openclean-pattern


Examples
========
We include several example notebooks in this repository that demonstrate possible use cases for **openclean-pattern**.


See also:
=========

* `OpenClean <https://github.com/VIDA-NYU/openclean-core>`__
* `OpenClean-Notebook <https://github.com/VIDA-NYU/openclean-notebook>`__
* `Datamart-Geo <https://gitlab.com/ViDA-NYU/datamart/datamart-geo>`__
