from abc import ABCMeta, abstractmethod

ALIGNER_LINGPY = 'LING'
ALIGNER_COMB = 'COMB'

ALIGNERS = [ALIGNER_LINGPY, ALIGNER_COMB]

class Aligner(object, metaclass=ABCMeta):
    def __init__(self, aligner):
        self.aligner = aligner if aligner in ALIGNERS else None
        if self.aligner is None:
            raise ValueError(aligner)

    @abstractmethod
    def get_aligned(self, rows, column=None):
        '''
        should take in all rows and return the aligned numpy array
        :param rows: tokenized list of rows (list)
        :params column: passed when encoded = True
        :return: nxm numpy array
        '''
        raise NotImplementedError()