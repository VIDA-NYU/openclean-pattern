from openclean_pattern.datatypes.base import SupportedDataTypes
from openclean_pattern.align.distance import Distance, DISTANCE_TDE

from string import punctuation
import numpy as np

class TdeDistance(Distance):
    def __init__(self):
        super(TdeDistance, self).__init__(DISTANCE_TDE)

    # distance b/w 2 rows:
    def get_distance(self, u, v):
        punc = punctuation+' '
        distance = 0
        for i in range(len(u)):
            if u[i] == SupportedDataTypes.GAP or v[i] == SupportedDataTypes.GAP:
                distance += 1
            elif (u[i] in punc and v[i] in punc) and u[i] == v[i]:
                distance += 0
            elif (u[i] in punc and v[i] in punc) and u[i] != v[i]:
                distance += 1
            elif (u[i] in punc and v[i] not in punc) or \
                (u[i] not in punc and v[i] in punc):
                distance += 1
            elif (u[i] not in punc and v[i] not in punc):
                nlu, nlv, ndu, ndv = 0, 0, 0, 0
                for j in u[i]:
                    if j.isalpha():
                        nlu += 1
                    elif j.isnumeric():
                        ndu += 1
                for j in v[i]:
                    if j.isalpha():
                        nlv += 1
                    elif j.isnumeric():
                        ndv += 1
                distance += (1-(np.minimum(nlu, nlv)+np.minimum(ndu, ndv))/np.maximum(len(u[i]), len(v[i])))

        return distance
