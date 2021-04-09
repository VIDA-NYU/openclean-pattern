# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Prefix searchable prefix tree implementation using pygtrie"""

from typing import Iterable, List, Optional, Tuple

import pygtrie
import string
import warnings


class PrefixTree(object):
    """Prefix Tree class to create a map using the provided vocabulary and prefix search it
    """
    def __init__(self, vocabulary: Iterable[Tuple[Iterable[str], str]], ignore_case: Optional[bool] = True):
        """builds the prefix trie using the provided vocabulary

        Parameters
        ----------
        vocabulary: Iterable
            Vocabulary to build tree from. Different lists of words in the
            vocabulary are associated with a type label.
        ignore_case: bool, default=True
            Perform case-insensitive matching if True.
        """
        self.ignore_case = ignore_case
        self.trie = pygtrie.StringTrie()
        for words, label in vocabulary:
            for word in words:
                if ignore_case:
                    word = word.lower()
                dom_word = self.trie._separator.join(word.split())
                if dom_word in self.trie:
                    if self.trie[dom_word][1] != label:
                        warnings.warn("duplicate pytrie entry '{}' with different label: '{}' found. Original label: {} is immutable, Ignoring duplicate.".format(word, label, self.trie[dom_word][1]))
                    continue
                self.trie[dom_word] = (word, label)

    def prefix_search(self, content_words: List[str], ignore_punc: Optional[bool] = True) -> Tuple[int, str]:
        """Identifies prefixe matches for the given word list from the vocabulary
        that was used to build the prefix tree.

        Returns the index of the last token that matches the prefix and the
        token type label. The result is (None, None) for no matches.

        Parameters
        ----------
        content_words: list
            the string to perform the search on
        ignore_punc: bool (default: True)
            searches through the content words ignoring any punctuations in between

        Returns
        -------
        tuple of int, str
        """
        punc = list(string.punctuation) + [' ']
        # Shortcut to access the trie separator.
        sep = self.trie._separator
        prefix_path = list()
        for i, token in enumerate(content_words):
            # Ignore punctuation tokens if the respective flag is True. We do
            # need to make sure, however, not to ignore leading puctuation
            # tokens.
            if ignore_punc and prefix_path:
                if token in punc and i < len(content_words)-1:
                    continue
            # Convert to lower case for case-insentive matching.
            if self.ignore_case:
                token = token.lower()
            # Get value for prefix from previous iteration from the prefix path.
            prefix = '{}{}{}'.format(prefix_path[-1][0], sep, token) if prefix_path else token
            prefix_in_trie = self.trie.has_node(prefix)
            if not prefix_in_trie:
                break
            # Get the label for the matched prefix. Note that the value is only
            # defined if the prefix matches a value (and not just a subtree).
            if prefix_in_trie & pygtrie.Trie.HAS_VALUE:
                _, label = self.trie.get(prefix)
            else:
                label = None
            prefix_path.append((prefix, i, label, prefix_in_trie))
        # Find maximum entry in the prefix path that points to a value.
        while prefix_path:
            _, index, label, prefix_in_trie = prefix_path.pop()
            if prefix_in_trie & pygtrie.Trie.HAS_VALUE:
                return index, label
        return None, None
