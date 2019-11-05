class LexError(Exception):
    def __init__(self, err, line=1, col=1):
        super().__init__('lex[{}:{}]: '.format(line, col) + err)


class ParseError(Exception):
    def __init__(self, err, line=1, col=1):
        super().__init__('parse[{}:{}]: '.format(line, col) + err)


class SemanticError(Exception):
    def __init__(self, err, line=1, col=1):
        super().__init__('semantic[{}:{}]: '.format(line, col) + err)

class PreprocessError(Exception):
    def __init__(self, err, line=1, col=1):
        super().__init__('preprocess[{}:{}]: '.format(line, col) + err)
