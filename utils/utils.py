import re
from openclean.datatypes import DateTime

class TypeChecker:
    def __init__(self):
        self.dt = DateTime()
        # todo: configurable using a config file?

    def has_numbers(self, inputString):
        return bool(re.search(r'\d', inputString))

    def character_comp_regex(self, s1, s2):
        # if self.dt.is_datetime(s2) != False:
        #     return self.dt.is_datetime(s2), 0

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

    def pattern_token_comp(self, pattern, width, token):
        if len(token) >= width[0] and len(token) <= width[1]:
            for i in range(min(len(token), len(pattern))):
                if pattern[i].upper() != token[i].upper():  # not case sensitive?
                    if pattern[i].upper() == 'X':
                        continue
                    else:
                        return False
            return True
        return False
