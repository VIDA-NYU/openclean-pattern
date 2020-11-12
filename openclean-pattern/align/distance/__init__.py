from abc import ABCMeta, abstractmethod

DISTANCE_ABSOLUTE = 'ABS'
DISTANCE_TDE = 'TDE'
DISTANCE_ETDE = 'ETDE'

DISTANCES = [DISTANCE_TDE, DISTANCE_ABSOLUTE, DISTANCE_ETDE]

class Distance(object, metaclass=ABCMeta):
    def __init__(self, dist):
        self.dist_type = dist if dist in DISTANCES else None
        if self.dist_type is None:
            raise ValueError(dist)

    @abstractmethod
    def get_distance(self, u, v):
        '''
        should take in 2 rows and return the distance (float) between them
        :param u: row1 (list)
        :param v: row2 (list)
        :return: distance (float)
        '''
        raise NotImplementedError()