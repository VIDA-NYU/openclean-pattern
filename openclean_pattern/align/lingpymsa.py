from openclean.align import Aligner, ALIGNER_LINGPY
from lingpy import mult_align
import numpy as np

class LingpyAligner(Aligner):
    def __init__(self):
        super(ALIGNER_LINGPY, self).__init__(ALIGNER_LINGPY)

    # get msa string. returns numpy.array
    def get_aligned(self, rows, column=None):
        return np.array(mult_align(rows))
