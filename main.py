import sys

import lex
import parse
import semantic

from error import ParseError, LexError

def main():

    lexer = lex.Lexer()

    if len(sys.argv) > 1:
        with open(sys.argv[1]) as fp:
            lines = [l.strip() for l in fp.readlines()]
            tokens = lexer.tokenize(lines)
            parser = parse.Parser(tokens)
            ast = parser.program()
            print(ast)
            analyzer = semantic.SemanticAnalyzer()
            symbols = analyzer.analyze(ast)
            print(symbols)
    else:
        try:
            while True:
                line = input('> ')
                tokens = lexer.tokenize([line])
                parser = parse.Parser(tokens)
                ast = parser.program()
                print(ast)
        except (EOFError, ParseError, LexError) as e:
            print(e)

if __name__ == '__main__':
    main()
