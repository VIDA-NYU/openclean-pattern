from openclean.tokenize import TOKENIZER_REGEX, TOKENIZER_SMART, TOKENIZERS
from openclean.tokenize.regex import RegexTokenizer
from openclean.tokenize.smart import SmartTokenizer

class TokenizerFactory(object):
    '''
    factory methods to create a tokenizer class object
    '''
    def __init__(self,
                 tokenizer: str = TOKENIZER_REGEX,
                 encode: bool = False,
                 ) -> None:
        if tokenizer not in TOKENIZERS:
            raise ValueError(tokenizer)
        if tokenizer == TOKENIZER_REGEX:
            tokenizer = RegexTokenizer()
        elif tokenizer == TOKENIZER_SMART:
            tokenizer = SmartTokenizer()
        self._tokenizer = tokenizer

    def get_tokenizer(self):
        return self._tokenizer