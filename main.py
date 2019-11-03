import sys

import lex
import parse
import semantic

from error import ParseError, LexError, SemanticError

class PyCC():
    lines = []
    lexer = lex.Lexer()
    parser = parse.Parser()
    analyzer = semantic.SemanticAnalyzer()

    def repl():
        while True:
            line = input('PyCC> ')
            op = PyCC.repl_cmds.get(line)
            if op:
                op()
            else:
                try:
                    ln, src = line.split(maxsplit=1)
                    ln = int(ln)
                    if ln > len(lines):
                        PyCC.lines += ['' for x in range(ln + 1)]
                        PyCC.lines[ln] = src
                except (ValueError, TypeError) as e:
                    PyCC.compile_line(line)



    def file(path=''):
        with open(path) as fp:
            PyCC.lines = [line.strip() for line in fp]
        PyCC.compile()


    def compile():
        tokens = PyCC.lexer.tokenize(PyCC.lines)
        ast = PyCC.parser.parse(tokens)
        sym = PyCC.analyzer.analyze(ast)

        print(tokens, '\n')
        print(ast, '\n')
        print(sym, '\n')


    def compile_line(line):
        tokens = PyCC.lexer.tokenize([line])
        ast = PyCC.parser.parse(tokens)
        sym = PyCC.analyzer.analyze(ast)

        print(tokens, '\n')
        print(ast, '\n')
        print(sym, '\n')


    def main():
        if len(sys.argv) > 1:
            PyCC.file()
        else:
            PyCC.repl()


    repl_cmds = {
            'exit': lambda: sys.exit(0),
            'run': compile,
            'clear': lambda: lines.clear()
    }


lines = []

lexer = lex.Lexer()
parser = parse.Parser()
analyzer = semantic.SemanticAnalyzer()

def evaluate_line(line):
    global lines
    global lexer
    global parser
    global analyzer
    try:
        ln, src = line.split(maxsplit=1)
        ln = int(ln)
        if ln > len(lines):
            lines += ['' for x in range(ln + 1)]
            lines[ln] = src
    except (TypeError, ValueError) as e:
        if line.strip() == 'eval':
            tokens = lexer.tokenize(lines)
            print(tokens, '\n')
            ast = parser.parse(tokens)
            print(ast, '\n')
            symbols = analyzer.analyze(ast)
            print(symbols, '\n')
        else:
            tokens = lexer.tokenize([line])
            print(tokens, '\n')
            ast = parser.parse(tokens)
            print(ast, '\n')
            symbols = analyzer.analyze(ast)
            print(symbols, '\n')

def main():
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1]) as fp:
                lines = [l.strip() for l in fp.readlines()]
        except (EOFError, ParseError, LexError, SemanticError) as e:
            print(e)
    else:
            while True:
                try:
                    line = input('> ')
                    # tokens = lexer.tokenize([line])
                    # parser = parse.Parser(tokens)
                    # ast = parser.program()
                    # print(ast)
                    # analyzer = semantic.SemanticAnalyzer()
                    # symbols = analyzer.analyze(ast)
                    # print(symbols)
                    evaluate_line(line)
                except (ParseError, LexError, SemanticError) as e:
                    print(e)

if __name__ == '__main__':
    try:
        PyCC.main()
    except (EOFError, KeyboardInterrupt) as e:
        print('Farewell')
