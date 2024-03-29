import re

from error import LexError

from collections import OrderedDict

class Lexer():

    token_names = OrderedDict()

    token_names['((int)|(char)|(float)|(void))\**'] = 'TK_TYPE'
    token_names[r'"(?:\\.|[^"\\])*"'] = 'TK_STRING'
    token_names['if'] = 'TK_IF'
    token_names['else'] = 'TK_ELSE'
    token_names['return'] = 'TK_RETURN'
    token_names['while'] = 'TK_WHILE'
    token_names['do'] = 'TK_DO'
    token_names['struct'] = 'TK_STRUCT'
    token_names['sizeof'] = 'TK_SIZEOF'
    token_names['[A-Za-z_][A-Za-z0-9_]*'] = 'TK_IDENTIFIER'
    #token_names['((0x[0-9A-Fa-f]+)|([0-9]+))'] = 'TK_INTEGER'
    #token_names['[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'] = 'TK_NUMBER'
    token_names['(0x[0-9A-Fa-f]+)|[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'] = 'TK_NUMBER'
    token_names['\".*?\"'] = 'TK_STRING'

    token_names['&&'] = 'TK_LAND'
    token_names['\|\|'] = 'TK_LOR'

    token_names['&'] = 'TK_AND'
    token_names['\|'] = 'TK_OR'

    token_names['<<'] = 'TK_LSHIFT'
    token_names['>>'] = 'TK_RSHIFT'

    token_names['\^'] = 'TK_XOR'
    token_names['~'] = 'TK_NOT'

    token_names['=='] = 'TK_EQEQUAL'
    token_names['>='] = 'TK_GEQUAL'
    token_names['<='] = 'TK_LEQUAL'

    token_names['='] = 'TK_EQUAL'

    token_names['>'] = 'TK_GREATER'
    token_names['<'] = 'TK_LESSER'

    token_names['\+\+'] = 'TK_DPLUS'
    token_names['--'] = 'TK_DMINUS'

    token_names['->'] = 'TK_ARROW'

    token_names['\+'] = 'TK_PLUS'
    token_names['-'] = 'TK_MINUS'

    token_names['\*'] = 'TK_STAR'
    token_names['/'] = 'TK_SLASH'

    token_names['!'] = 'TK_BANG'

    token_names['\['] = 'TK_LBRACK'
    token_names['\]'] = 'TK_RBRACK'

    token_names['\('] = 'TK_LPAR'
    token_names['\)'] = 'TK_RPAR'

    token_names['\{'] = 'TK_LBRACE'
    token_names['\}'] = 'TK_RBRACE'

    token_names['\?'] = 'TK_QMARK'
    token_names[':'] = 'TK_COLON'

    token_names[';'] = 'TK_ENDLINE'

    token_names[','] = 'TK_COMMA'
    token_names['\.'] = 'TK_DOT'

    def tokenize(self, lines):
        tokens = []
        for i,line in enumerate(lines):
            col = 1
            while line:
                key = None
                for r in Lexer.token_names.keys():
                    m = re.match(r, line)
                    if m:
                        line = line[m.end() : ].strip()
                        token = (Lexer.token_names[r], m.group(), i + 1, col)
                        tokens.append(token)
                        col += m.end() - m.start()
                        break
                if not m:
                    raise LexError('invalid token.', i + 1, col)
        tokens.append(('TK_EOF', None, len(lines), 1))
        return tokens
