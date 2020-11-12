import pygtrie, re

class PrefixTree():
    def __init__(self, words):
        self.trie = self.build_trie(domain_words=words)

    def prefix_search(self, content, abbreviations=False):
        trie = self.trie

        # todo: account for <apostrophe 's> similarly
        # split on everything except dots if abbreviations = True
        regex = r'[\w.]+' if abbreviations else r'[\w]+'
        content_words = re.findall(regex, content)
        content_words = [item for sublist in [j.split('_') for j in content_words] for item in sublist] # handle _ separately

        phrases = set()
        discovered_prefixes = set()
        old_prefix = list()
        for possible_prefix in content_words:
            #has_node returns 1(HAS_VALUE) if the exact key is found, 2(HAS_SUBTRIE) if the key is a sub trie,
            # 3 if it's both 0 if it's none
            #https://pygtrie.readthedocs.io/en/latest/#pygtrie.Trie.has_node

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
        trie = pygtrie.StringTrie()
        for word in domain_words:
            dom_word = trie._separator.join(word.split())
            if trie.has_key(dom_word):
                dom_words = trie.get(dom_word)
                dom_words.update([word])
            else:
                trie[dom_word] = {word}
        return trie