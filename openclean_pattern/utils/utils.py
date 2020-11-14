# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2020 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""A collection of useful utility methods"""

import re
from openclean_pattern.datatypes.resolver import DateTimeResolver
from abc import ABCMeta, abstractmethod
import random
import bisect
from collections import Counter

### Comparators

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


class DateComparator(Comparator):

    def __init__(self):
        self.dt = DateTimeResolver()

    def compare(self, a, b):
        if self.dt.is_datetime(a) != False:
            return self.dt.is_datetime(b), 0


class StringComparator(Comparator):
    def character_comp_regex(self, s1, s2):
        smaller_size = min(len(s1), len(s2))
        new_string = ''
        for i in range(smaller_size):
            if s1[i] == s2[i]:
                new_string += s1[i]
            else:
                new_string += 'X'
        for j in range(abs(len(s1) - len(s2))):
            new_string += 'X'

        return new_string, new_string.count('X') / len(new_string)


class PatternComparator(Comparator):
    def compare(self, a, b, meta=None):
        raise NotImplementedError()
    # def compare(self, pattern, token):(self, pattern, width, token):
    #     if len(token) >= width[0] and len(token) <= width[1]:
    #         for i in range(min(len(token), len(pattern))):
    #             if pattern[i].upper() != token[i].upper():  # not case sensitive?
    #                 if pattern[i].upper() == 'X':
    #                     continue
    #                 else:
    #                     return False
    #         return True
    #     return False


def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))


### Samplers

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
        rnd = random.Random(self.random_state).random() * self.totals[-1]
        return bisect.bisect_right(self.totals, rnd)

    def __call__(self):
        """samples n (or n*total_inputs, if n is a fraction) times and returns the sampled frequencies as a counter

        Returns
        -------
            sampled list of rows
        """
        sample = Counter()
        n = self.totals[-1] * self.n if self.frac else self.n
        keys = list(self.iterable.keys())
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
        n = len(self.iterable) * self.n if self.frac else self.n
        return random.Random(self.random_state).sample(self.iterable, n)
