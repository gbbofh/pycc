import sys
import math

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
                    if ln > len(PyCC.lines):
                        PyCC.lines += ['' for x in range(ln + 1)]
                    PyCC.lines[ln] = src
                except (ValueError, TypeError) as e:
                    PyCC.compile_line(line)



    def file(path=''):
        with open(path) as fp:
            PyCC.lines = [line.strip() for line in fp]
        PyCC.compile()


    def compile():
        try:
            tokens = PyCC.lexer.tokenize(PyCC.lines)
            ast = PyCC.parser.parse(tokens)
            sym = PyCC.analyzer.analyze(ast)

            print(tokens, '\n')
            print(ast, '\n')
            print(sym, '\n')
        except (LexError, ParseError, SemanticError) as e:
            print(e)


    def compile_line(line):
        try:
            tokens = PyCC.lexer.tokenize([line])
            ast = PyCC.parser.parse(tokens)
            sym = PyCC.analyzer.analyze(ast)

            print(tokens, '\n')
            print(ast, '\n')
            print(sym, '\n')
        except (LexError, ParseError, SemanticError) as e:
            print(e)


    def main():
        if len(sys.argv) > 1:
            PyCC.file()
        else:
            PyCC.repl()


    def print_lines():
        k = int(math.log(len(PyCC.lines) + 1))
        for i, ln in enumerate(PyCC.lines):
            if ln:
                print('{num:{width}}'.format(num=i, width=k), ln)


    repl_cmds = {
            'run': compile,
            'print': print_lines,
            'clear': lambda: PyCC.lines.clear(),
            'exit': lambda: sys.exit(0),
    }


if __name__ == '__main__':
    try:
        PyCC.main()
    except (EOFError, KeyboardInterrupt) as e:
        print('Farewell')
