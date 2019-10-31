import sys

import lex
import parse
import semantic

from error import ParseError, LexError, SemanticError

def main():

    lexer = lex.Lexer()

    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1]) as fp:
                lines = [l.strip() for l in fp.readlines()]
                tokens = lexer.tokenize(lines)
                parser = parse.Parser(tokens)
                ast = parser.program()
                print(ast)
                analyzer = semantic.SemanticAnalyzer()
                symbols = analyzer.analyze(ast)
                print(symbols)
        except (EOFError, ParseError, LexError, SemanticError) as e:
            print(e)
    else:
            while True:
                try:
                    line = input('> ')
                    tokens = lexer.tokenize([line])
                    parser = parse.Parser(tokens)
                    ast = parser.program()
                    print(ast)
                    analyzer = semantic.SemanticAnalyzer()
                    symbols = analyzer.analyze(ast)
                    print(symbols)
                except (ParseError, LexError, SemanticError) as e:
                    print(e)

if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt) as e:
        print('Farewell')
