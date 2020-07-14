from openclean.align.combinatorics import CombAligner
from openclean.align.lingpymsa import LingpyAligner
from openclean.align import ALIGNER_LINGPY, ALIGNER_COMB, ALIGNERS
from openclean.align.distance import DISTANCE_TDE

class AlignerFactory(object):
    '''
    factory methods to create an aligner class object
    '''
    def __init__(self,
                 aligner: str = ALIGNER_COMB,
                 distance: str = DISTANCE_TDE,
                 ) -> None:
        if aligner not in ALIGNERS and aligner is not None:
            raise ValueError(aligner)
        if aligner == ALIGNER_COMB:
            aligner = CombAligner(distance=distance)
        elif aligner == ALIGNER_LINGPY:
            aligner = LingpyAligner()
        self._aligner = aligner

    def get_aligner(self):
        return self._aligner