# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""factory methods for the regex module"""

from openclean_pattern.regex.compiler import COMPILER_DEFAULT, DefaultRegexCompiler


class CompilerFactory(object):
    """factory methods to create a compiler class object
    """

    @staticmethod
    def create_compiler(compiler):
        """Returns the compile object if the input string matches the compiler identifier

        Parameters
        ----------
        compiler: str
            name string of the compiler
        """
        if compiler == COMPILER_DEFAULT:
            return DefaultRegexCompiler()

        raise ValueError('compiler: {} not found'.format(compiler))
