# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Prefix searchable prefix tree implementation using pygtrie"""
import pygtrie, string


class PrefixTree(object):
    """Prefix Tree class to create a map using the provided vocabulary and prefix search it
    """
    def __init__(self, words):
        """builds the prefix trie using the provided vocabulary

        Parameters
        ----------
        words: Iterable
            vocabulary to build tree from
        """
        self.trie = self.build_trie(domain_words=words)

    def prefix_search(self, content_words, ignore_punc=True):
        """ identifies prefixes from the vocabulary present in the content string.

        Parameters
        ----------
        content_words: list
            the string to perform the search on
        ignore_punc: bool (default: True)
            searches through the content words ignoring any punctuations in between

        Returns
        -------
            set
        """
        trie = self.trie

        phrases = set()
        discovered_prefixes = set()
        old_prefix = list()
        punc = list(string.punctuation) + [' ']

        for i, possible_prefix in enumerate(content_words):

            if ignore_punc:
                if possible_prefix in punc and i < len(content_words)-1:
                    continue

            # has_node returns 1(HAS_VALUE) if the exact key is found, 2(HAS_SUBTRIE) if the key is a sub trie,
            # 3 if it's both 0 if it's none
            # https://pygtrie.readthedocs.io/en/latest/#pygtrie.Trie.has_node
            prefix_in_trie = trie.has_node(possible_prefix)
            if prefix_in_trie & pygtrie.Trie.HAS_VALUE:
                prefix = trie.get(possible_prefix)
                discovered_prefixes.update(prefix)

            deep_copy_phrases = set(phrases)

            # Check if extending the phrases with the current word in content is a subtrie or key. And
            # Remove the word if it is not a subtrie as we are interested only in continuos words in the content
            for phrase in deep_copy_phrases:
                phrases.remove(phrase)
                extended_phrase = phrase + trie._separator + possible_prefix
                phrase_in_trie = trie.has_node(extended_phrase)

                if phrase_in_trie & pygtrie.Trie.HAS_VALUE:
                    prefix = trie.get(extended_phrase)
                    discovered_prefixes.update(prefix)
                    try:
                        old_prefix.append(trie.get(phrase))
                        [discovered_prefixes.discard(op) for op in old_prefix]
                    except:
                        pass

                if phrase_in_trie & pygtrie.Trie.HAS_SUBTRIE:
                    phrases.add(extended_phrase)
                    try:
                        old_prefix.append(trie.get(possible_prefix))
                    except:
                        pass

            if prefix_in_trie & pygtrie.Trie.HAS_SUBTRIE:
                phrases.add(possible_prefix)

        return discovered_prefixes

    def build_trie(self, domain_words):
        """build a trie using the vocabulary provided

        Parameters
        ----------
        domain_words: Iterable
            the vocabulary words that will be used to build the trie
        Returns
        -------
            pygtrie.StringTrie
        """
        trie = pygtrie.StringTrie()
        for word in domain_words:
            dom_word = trie._separator.join(word.split())
            if trie.has_key(dom_word):
                dom_words = trie.get(dom_word)
                dom_words.update([word])
            else:
                trie[dom_word] = {word}
        return trie
