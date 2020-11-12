from openclean.tokenize import Tokenizer, TOKENIZER_REGEX
from openclean.regex.compiler import RegexCompiler
import re

class RegexTokenizer(Tokenizer):
    def __init__(self, regex=r"[\w]+|[^\w]"):
        super(RegexTokenizer, self).__init__(TOKENIZER_REGEX)
        self.regex = regex

    def tokenize(self, column):
        column = super().replace_hyphens(column)
        return column \
            .apply(lambda x: re.findall(r"[\w]+|[^\w]", x)) \
            .apply(lambda x: [item for sublist in [re.split('(_)', j) for j in x] for item in sublist])

    def tokenize_row(self, x):
        x = super().replace_hyphens_row(x)
        x = re.findall(r"[\w]+|[^\w]", x)
        return [item for sublist in [re.split('(_)', j) for j in x] for item in sublist]

    def encode(self, column, freq):
        col = self.tokenize(column)
        return RegexCompiler.compile(col.tolist(), freq)
