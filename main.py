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
            line = input('PyCC> ').strip()
            op = PyCC.repl_cmds.get(line)
            if op:
                op()
            else:
                try:
                    ln, src = line.split(maxsplit=1)
                    ln = int(ln)
                    if ln > len(PyCC.lines):
                        PyCC.lines += ['' for x in range(ln + 2)]
                    PyCC.lines[ln + 1] = src
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

            PyCC.print_results(tokens, ast, sym)

        except (LexError, ParseError, SemanticError) as e:
            print(e)


    def compile_line(line):
        try:
            tokens = PyCC.lexer.tokenize([line])
            ast = PyCC.parser.parse(tokens)
            sym = PyCC.analyzer.analyze(ast)

            PyCC.print_results(tokens, ast, sym)

        except (LexError, ParseError, SemanticError) as e:
            print(e)


    def _print_ast_node(node, level = 0):
        if isinstance(node, tuple):
            for e in node:
                PyCC._print_ast_node(e, level + 1)
        else:
            print(' ' * level, node)


    def print_results(tokens, ast, symbols):
        print('Tokens:')
        for t in tokens:
            print(t)
        print('\n')

        print('Syntax Tree:')
        #print(ast)
        PyCC._print_ast_node(ast)
        print('\n')

        print('Global Symbols:')
        for sym in symbols:
            print('{} : {}'.format(sym, symbols[sym]))
        print('\n')


    def main():
        if len(sys.argv) > 1:
            PyCC.file(sys.argv[1])
        else:
            PyCC.repl()


    def print_lines():
        k = int(math.log(len(PyCC.lines) + 1))
        for i, ln in enumerate(PyCC.lines):
            if ln:
                print('{num:{width}}'.format(num=i, width=k), ln)


    repl_cmds = {
            'run': compile,
            'source': print_lines,
            'clear': lambda: PyCC.lines.clear(),
            'exit': lambda: sys.exit(0),
    }


if __name__ == '__main__':
    try:
        PyCC.main()
    except (EOFError, KeyboardInterrupt) as e:
        print('Farewell')
