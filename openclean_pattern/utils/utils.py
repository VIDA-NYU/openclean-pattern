# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""A collection of useful utility methods"""

import re
from abc import ABCMeta, abstractmethod
import random
import bisect
from collections import Counter


# -- Comparators --------------------------------------------------------------

class Comparator(metaclass=ABCMeta):
    """Compares different dataitems
    """

    @abstractmethod
    def compare(self, a, b, meta=None):
        """Compares a with b and returns True if a and b are equal. The comparison can involve any
        extra meta information that the user wants to consider

        Parameters:
        ----------
        a: Any
            the datatype to compare
        b: Any
            the datatype to compare against
        meta: Any (Optional)
            any extra information used in the comparison

        Returns
        -------
            bool
        """
        raise NotImplementedError()


class StringComparator(Comparator):
    """Class of useful string comparison methods
    """

    @staticmethod
    def compare_strings(s1, s2, ambiguous_char='X'):
        """
        Compares two strings in sequence of characters and replaces distinct
        characters with ambiguous character. Then returns the new string along
        with an ambiguity ratio

        Parameters
        ----------
        s1 : str
            string 1
        s2 : str
            string 2
        ambiguous_char: str
            replaces the distinct characters with

        Returns
        -------
            str, float
        """
        smaller_size = min(len(s1), len(s2))
        new_string = ''
        for i in range(smaller_size):
            if s1[i] == s2[i]:
                new_string += s1[i]
            else:
                new_string += ambiguous_char
        for j in range(abs(len(s1) - len(s2))):
            new_string += ambiguous_char

        ambiguity = new_string.count(ambiguous_char) / len(new_string) if len(new_string) > 0 else 0
        return new_string, ambiguity

    @staticmethod
    def substring_finder(string1, string2):
        anslist = []
        len1, len2 = len(string1), len(string2)
        for i in range(len1):
            match = ""
            for j in range(len2):
                if (i + j < len1 and string1[i + j] == string2[j]):
                    match += string2[j]
                else:
                    answer = match
                    if answer != '' and len(answer) > 1:
                        anslist.append(answer)
                    match = ""
            if match != '':
                anslist.append(match)

        return anslist


def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))


# -- Samplers -----------------------------------------------------------------

class Sampler(metaclass=ABCMeta):
    """Class to sample an input iterable. This was necessary because pandas.sample sampling can be slow."""

    def __init__(self, iterable, n=1):
        """initizlizes the Sampler class

        Parameters
        ----------
        iterable: Iterable
            the iterable class object which has data to be sampled
        n: float
            the proportion or number of records to sample
        """
        self.iterable = iterable
        self.n = n
        self.frac = 0 <= n <= 1

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """Method to sample the input iterable sequence
        """
        raise NotImplementedError()

    def sample(self):
        """a convenience sample method
        """
        return self.__call__()


class WeightedRandomSampler(Sampler):
    """Implements weighted random sampling using the distribution provided collections.Counter object.
    Based on the work: https://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python/

    Note: if a Counter or dict of type {value:frequency} is passed in, there is no rowidx information tied to
    the sampled series and this can possibly require an extra lookup during anomaly detection
        """

    def __init__(self, weights, n=1, random_state=None):
        """initizlizes the WeightedRandomSampler class

        Parameters
        ----------
        weights: collections.Counter
            the counter object in the format key:frequency
        n: float
            the proportion or number of records to sample
        random_state: int (default: None)
            the seed value for the pseudo random number generator
        """
        super(WeightedRandomSampler, self).__init__(weights, n)
        self.random_state = random_state
        self.totals = []  # cumulative sum
        running_total = 0

        for w in weights.values():
            running_total += w
            self.totals.append(running_total)

    def next(self):
        """selects a new randomly sampled value from the input series based on their weight distribution and returns
        the respective index

        Returns
        -------
            int
        """
        rnd = random.random() * self.totals[-1]
        return bisect.bisect_right(self.totals, rnd)

    def __call__(self):
        """samples n (or n*total_inputs, if n is a fraction) times and returns the sampled frequencies as a counter

        Returns
        -------
            sampled list of rows
        """
        sample = Counter()
        n = int(self.totals[-1] * self.n) if self.frac else int(self.n)
        keys = list(self.iterable.keys())
        random.seed(self.random_state)
        for _c in range(n):
            sample[keys[self.next()]] += 1
        return WeightedRandomSampler.counter_to_list(sample)

    @staticmethod
    def counter_to_list(counter):
        """ method to create a series list from a counter object

        Parameters
        ----------
        counter: collections.Counter
            the counter object to convert to a list

        Returns
        -------
            list of values
        """
        series = list()
        for k, v in counter.items():
            for _ in range(v):
                series.append(k)
        return series


class RandomSampler(Sampler):
    """Class to randomly sample an input iterable. This was necessary because pandas.sample samples a dataframe
    which can be slow.

    Note: if a Counter or dict of type {value:frequency} is passed in, there is no rowidx information tied to
    the sampled series and this can possibly require an extra lookup during anomaly detection
    """

    def __init__(self, iterable, n=1, random_state=None):
        """initizlizes the Random Sampler class

        Parameters
        ----------
        iterable: Iterable
            the iterable class object which has data to be sampled
        n: float
            the proportion or number of records to sample
        random_state: int (default: None)
            the seed value for the pseudo random number generator
                    """
        super(RandomSampler, self).__init__(iterable, n)
        self.random_state = random_state

    def __call__(self, *args, **kwargs):
        """Method to sample the input iterable sequence

         Returns
        -------
            sampled list of rows
        """
        random.seed(self.random_state)
        n = int(len(self.iterable) * self.n) if self.frac else int(self.n)
        return random.sample(self.iterable, n)


class Distinct(Sampler):
    """Class to select only the distinct values from the input iterable"""

    def __init__(self, iterable):
        """initizlizes the Distinct class

        Parameters
        ----------
        iterable: Iterable
            the iterable class object which has data to be sampled
        """
        super(Distinct, self).__init__(iterable, 1)

    def __call__(self, *args, **kwargs):
        """Method to distinct-ify the input iterable sequence

        Returns
        -------
            distinct list of rows
        """
        return list(set(self.iterable))


# -- Helper methods -----------------------------------------------------------------

def list_contains_list(o, tree_types=list):
    """checks is list contains more lists"""
    if isinstance(o, tree_types):
        for v in o:
            if isinstance(v, tree_types):
                return True
    elif not isinstance(o, tree_types):
        #  ignore values that arent lists themselves
        return True

    return False