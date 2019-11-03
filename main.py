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


if __name__ == '__main__':
    try:
        PyCC.main()
    except (EOFError, KeyboardInterrupt) as e:
        print('Farewell')
