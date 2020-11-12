from openclean.align.distance.absolute import AbsoluteDistance
from openclean.align.distance.tde import TdeDistance
from openclean.align.distance.tde_encoded import EtdeDistance
from openclean.align.distance import DISTANCE_TDE, DISTANCE_ETDE, DISTANCE_ABSOLUTE, DISTANCES

class DistanceFactory(object):
    '''
    factory methods to create a distance class object
    '''
    def __init__(self,
                 distance: str = DISTANCE_TDE,
                 ) -> None:
        if distance not in DISTANCES:
            raise ValueError(distance)
        if distance == DISTANCE_TDE:
            dist = TdeDistance()
        elif distance == DISTANCE_ABSOLUTE:
            dist = AbsoluteDistance()
        elif distance == DISTANCE_ETDE:
            dist = EtdeDistance()
        self._distance = dist

    def get_distance(self):
        return self._distance