# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

""" Important to replace hyphen/dash because - is the gap character for multiple sequence alignment
"""
# NEW_HYPHEN_SYMBOL = '^'
# GAP_SYMBOL = '^'

# sequence alignment gap symbol
MSA_GAP_SYMBOL = '&zwnj;' # zero width non joiner special space character (&#8204;)
