from openclean_pattern.regex import *
from openclean_pattern.datatypes.base import SupportedDataTypes #GAP_SYMBOL
from openclean_pattern.align.distance import Distance, DISTANCE_ETDE

import re
from string import punctuation
import numpy as np

class EtdeDistance(Distance):
    def __init__(self):
        super(EtdeDistance, self).__init__(DISTANCE_ETDE)

    # distance b/w 2 rows:
    def get_distance(self, u, v):

        punc = [PUNCTUATION] #punctuation+' '
        distance = 0

        for ui, vi in zip(u, v):
            if ui.get_type() == GAP_SYMBOL or vi.get_type() == GAP_SYMBOL:
                distance += 1
            elif (ui.get_type() in punc and vi.get_type() in punc) and ui.get_token_str() == vi.get_token_str():
                distance += 0
            elif (ui.get_type() in punc and vi.get_type() in punc) and ui.get_token_str() != vi.get_token_str():
                distance += 1
            elif (ui.get_type() in punc and vi.get_type() not in punc) or \
                (ui.get_type() not in punc and vi.get_type() in punc):
                distance += 1
            elif (ui.get_type() not in punc and vi.get_type() not in punc):
                if ui.get_type() == vi.get_type() and \
                    ui.get_type() not in [ALPHANUM, ALPHA, DIGIT] and \
                    vi.get_type() not in [ALPHANUM, ALPHA, DIGIT]: # if they aren't punctuations and belong to the same supported data type class / are intermediate representations e.g. myXXX
                    distance += 0
                else:
                    nlu, nlv, ndu, ndv = 0, 0, 0, 0
                    for j in ui.get_token_str():
                        if j.isalpha():
                            nlu += 1
                        elif j.isnumeric():
                            ndu += 1
                    for j in vi.get_token_str():
                        if j.isalpha():
                            nlv += 1
                        elif j.isnumeric():
                            ndv += 1
                    distance += (1-(np.minimum(nlu, nlv)+np.minimum(ndu, ndv))/np.maximum(len(ui.get_token_str()), len(vi.get_token_str())))

        return distance
