from enum import IntEnum
from error import ParseError

class Precedence(IntEnum):
    NONE =          0
    ASSIGNMENT =    1
    TERNARY =       2
    OR =            3
    AND =           4
    BIN_OR =        5
    BIN_XOR =       6
    BIN_AND =       7
    EQUALITY =      8
    COMPARISON =    9
    SHIFT =         10
    TERM =          11
    FACTOR =        12
    UNARY =         13
    CALL =          14
    PRIMARY =       15

class Parser():


    def __init__(self, tokens=[]):
        self.tokens = tokens
        if tokens:
            self.prev = tokens[0]


    def type_number(self):
        f = 0
        if 'x' in self.prev[1] or 'X' in self.prev[1]:
            f = int(self.prev[1], 0)
        else:
            f = float(self.prev[1])
        return ('NUMBER', f)


    def type_string(self):
        s = str(self.prev[1][1 : -1])
        return ('STRING', s)


    def type_void(self):
        return ('VOID', None)


    def variable(self):
        return ('VARIABLE', self.prev[1])


    def group(self):
        if self.tokens[0][0] == 'TK_TYPE':
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            t = self.prev[1]
            if not self.tokens[0][0] == 'TK_RPAR':
                raise ParseError('expected \')\' following type')
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            expr = self.expression();
            return ('CAST', t, expr)
        expr = ('GROUP', self.expression())
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        return expr


    def call_args(self):
        params = tuple()
        if self.tokens[0][0] != 'TK_RPAR':
            while True:

                if len(params) > 255:
                    line, col = self.tokens[0][2], self.tokens[0][3]
                    raise ParseError('too many arguments in list', line, col)

                params += (self.expression(),)

                if not self.tokens[0][0] == 'TK_COMMA':
                    break
                self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        if not self.tokens[0][0] == 'TK_RPAR':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \')\'', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        return params


    def call(self, left):
        args = self.call_args()
        left = (left[1])
        return ('CALL', left, args)


    def unary(self):
        unary_ops = {
                'TK_MINUS': 'NEGATE',
                'TK_BANG': 'BANG',
                'TK_NOT': 'BITWISE_NOT',
                'TK_AND': 'REFERENCE',
                'TK_STAR': 'DEREFERENCE',
                'TK_SIZEOF': 'SIZEOF'
        }
        op = self.prev[0]
        expr = self.parse_precedence(Precedence.UNARY)
        return (unary_ops[op], expr)


    def pre_op(self):
        ops = {
                'TK_DPLUS': 'PREINCREMENT',
                'TK_DMINUS': 'PREDECREMENT'
        }
        op = self.prev[0]
        expr = self.parse_precedence(Precedence.UNARY)
        return (ops[op], expr)


    def post_op(self, left):
        ops = {
                'TK_DPLUS': 'POSTINCREMENT',
                'TK_DMINUS': 'POSTDECREMENT'
        }
        op = self.prev[0]
        return (ops[op], left)


    def binary(self, left):
        binary_ops = {
                'TK_PLUS':      'ADD',
                'TK_MINUS':     'SUB',
                'TK_STAR':      'MULT',
                'TK_SLASH':     'DIV',

                'TK_AND':       'BITWISE_AND',
                'TK_OR':        'BITWISE_OR',
                'TK_XOR':       'BITWISE_XOR',
                'TK_LSHIFT':    'LEFTSHIFT',
                'TK_RSHIFT':    'RIGHTSHIFT',

                'TK_EQUAL':     'ASSIGN',

                'TK_EQEQUAL':   'EQUAL',

                'TK_GEQUAL':    'GEQUAL',
                'TK_LEQUAL':    'LEQUAL',
                'TK_NEQUAL':    'NEQUAL',
                'TK_GREATER':   'GREATER',
                'TK_LESSER':    'LESSER',

                'TK_LAND':      'LOGICAL_AND',
                'TK_LOR':       'LOGICAL_OR'
        }
        op = self.prev[0]
        rule = Parser.rule[op]
        expr = self.parse_precedence(rule[2] + 1)
        return (binary_ops[op], left, expr)


    def ternary(self, lhs):
        op = self.prev[0]
        rule = Parser.rule[op]
        expr = self.parse_precedence(rule[2] + 1)

        colon, self.tokens = self.tokens[0], self.tokens[1 : ]
        self.prev = colon

        rule = Parser.rule[colon[0]]
        expr1 = self.parse_precedence(rule[2] + 1)

        return ('TERNARY', lhs, expr, expr1)


    def parse_precedence(self, precedence):
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        rule = Parser.rule[self.prev[0]][0]
        if not rule:
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('bad rule entry, or token', line, col)

        # Since we have to get the function dynamically from
        # the lookup table, we will have to manually pass
        # the reference to the Parser instance
        # to the function as a parameter.
        lhs = rule(self)

        while precedence <= Parser.rule[self.tokens[0][0]][2]:
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            rule = Parser.rule[self.prev[0]][1]
            lhs = rule(self, lhs)

        return lhs


    def expression(self):
        return self.parse_precedence(Precedence.ASSIGNMENT)


    def expression_statement(self):
        expr = self.expression()
        if not self.tokens[0][0] == 'TK_ENDLINE':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \';\' following expression', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        return expr


    def block_statement(self):

        statements = tuple()
        while self.tokens[0][0] != 'TK_RBRACE':
            statements = statements + (self.declaration(),)

        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        return ('BLOCK', statements)


    def return_statement(self):
        stmt = self.expression()
        if not self.tokens[0][0] == 'TK_ENDLINE':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \';\' following expression', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        return ('RETURN', stmt)


    def if_statement(self):
        if not self.tokens[0][0] == 'TK_LPAR':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \'(\'', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        expr = self.expression()
        if not self.tokens[0][0] == 'TK_RPAR':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \')\'', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        statement = self.statement()
        eblock = None

        while self.tokens[0][0] == 'TK_ELSE':
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            eblock = self.statement()

        return ('IF', expr, statement, eblock)


    def while_statement(self):
        if not self.tokens[0][0] == 'TK_LPAR':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \'(\'', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        expr = self.expression()
        if not self.tokens[0][0] == 'TK_RPAR':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \')\'', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        statement = self.statement()

        return ('WHILE', expr, statement)


    def do_while_statement(self):
        statement = self.statement()

        if not self.tokens[0][0] == 'TK_WHILE':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected keyword \'while\'', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        if not self.tokens[0][0] == 'TK_LPAR':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \'(\'', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        expr = self.expression()
        if not self.tokens[0][0] == 'TK_RPAR':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \')\'', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        if not self.tokens[0][0] == 'TK_ENDLINE':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \';\' following expression', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        return ('DO_WHILE', expr, statement)


    def for_statement(self):
        pass


    def statement(self):
        statement_types = {
                'TK_DO':        self.do_while_statement,
                'TK_WHILE':     self.while_statement,
                'TK_IF':        self.if_statement,
                'TK_LBRACE':    self.block_statement,
                'TK_RETURN':    self.return_statement,
                'TK_ENDLINE':   lambda: ('EMPTY',)
        }
        if self.tokens[0][0] in statement_types:
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            rule = self.prev[0]
            return statement_types[rule]()
        return self.expression_statement()


    def variable_decl(self, type_info):
        expr = None
        name = self.prev[1]

        if self.tokens[0][0] == 'TK_EQUAL':
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            expr = self.expression()

        if not self.tokens[0][0] == 'TK_ENDLINE':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \';\' following declaration', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        return ('DECLARE', name, type_info, expr)


    def parameter_list(self):
        params = tuple()
        if self.tokens[0][0] != 'TK_RPAR':
            while True:

                if len(params) > 255:
                    line, col = self.tokens[0][2], self.tokens[0][3]
                    raise ParseError('too many arguments in list', line, col)

                if not self.tokens[0][0] == 'TK_TYPE':
                    line, col = self.tokens[0][2], self.tokens[0][3]
                    raise ParseError('expected type', line, col)

                self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
                type_info = self.prev[1]

                if not self.tokens[0][0] == 'TK_IDENTIFIER':
                    line, col = self.tokens[0][2], self.tokens[0][3]
                    raise ParseError('expected identifier name', line, col)

                self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
                name = self.prev[1]

                params += (('PARAMETER', name, type_info),)

                if not self.tokens[0][0] == 'TK_COMMA':
                    break
                self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        return params


    def function_decl(self, type_info):
        params = None
        body = None
        name = self.prev[1]

        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        params = self.parameter_list()
        if not self.tokens[0][0] == 'TK_RPAR':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \')\' following parameters', line, col)

        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ] # Consume )

        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        if self.prev[0] == 'TK_LBRACE':
            body = self.block_statement()
        elif self.prev[0] != 'TK_ENDLINE':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected function body or \';\'', line, col)

        if not body:
            return ('DECL_FUNC', name, type_info, params)

        return ('FUNCTION', name, type_info, params, body)


    def function_variable_decl(self):
        expr = None
        type_info = self.prev[1]

        if not self.tokens[0][0] == 'TK_IDENTIFIER':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected identifier name', line, col)

        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        name = self.prev[1]

        if type_info == 'struct':
            type_info += ' ' + name

        if self.tokens[0][0] == 'TK_IDENTIFIER':
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            name = self.prev[1]

        if self.tokens[0][0] == 'TK_LPAR':
            return self.function_decl(type_info)
        elif type_info.startswith('struct') and name not in type_info:
            return self.variable_decl((type_info))
        elif type_info.startswith('struct'):
            return self.struct_decl(type_info)
        else:
            return self.variable_decl(type_info)
            #line, col = self.tokens[0][2], self.tokens[0][3]
            #raise ParseError('expected declaration', line, col)


    def struct_decl_members(self):
        members = tuple()
        while self.tokens[0][0] != 'TK_RBRACE':

            if not self.tokens[0][0] == 'TK_TYPE':
                line, col = self.tokens[0][2], self.tokens[0][3]
                raise ParseError('expected type in member declaration', line, col)
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            type_info = self.prev[1]

            if not self.tokens[0][0] == 'TK_IDENTIFIER':
                line, col = self.tokens[0][2], self.tokens[0][3]
                raise ParseError('expected identifier name', line, col)
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            name = self.prev[1]

            if not self.tokens[0][0] == 'TK_ENDLINE':
                line, col = self.tokens[0][2], self.tokens[0][3]
                raise ParseError('expected \';\' after ', name, line, col)
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

            members += ('MEMBER', name, type_info)
        return members


    def struct_decl(self, name):
        members = tuple()

        #self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        #name = self.prev[1]
        #if not self.tokens[0][0] == 'TK_LBRACE':
        #    self.prev, self.tokens = self.tokens[0], self.tokens[1 : ] # ;
        #    return ('DECL_STRUCT', name, members)
        #self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        # TODO: parse assignment
        if self.tokens[0][0] == 'TK_LBRACE':
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            members = self.struct_decl_members()
        # while self.tokens[0][0] != 'TK_RBRACE':

        #     if not self.tokens[0][0] == 'TK_TYPE':
        #         line, col = self.tokens[0][2], self.tokens[0][3]
        #         raise ParseError('expected type', line, col)
        #     self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        #     type_info = self.prev[1]

        #     if not self.tokens[0][0] == 'TK_IDENTIFIER':
        #         line, col = self.tokens[0][2], self.tokens[0][3]
        #         raise ParseError('expected identifier name', line, col)
        #     self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        #     name = self.prev[1]

        #     if not self.tokens[0][0] == 'TK_ENDLINE':
        #         line, col = self.tokens[0][2], self.tokens[0][3]
        #         raise ParseError('expected \';\' after ', name, line, col)
        #     self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        #     members += ('MEMBER', name, type_info)
            # self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            # TODO: parse struct members

            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        if not self.tokens[0][0] == 'TK_ENDLINE':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected \';\' following declaration', line, col)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]

        return ('STRUCT', name, members)


    def declaration(self):
        decl = None
        declaration_types = {
                'TK_TYPE':  self.function_variable_decl,
                'TK_STRUCT': self.function_variable_decl
        }
        if self.tokens[0][0] in declaration_types:
            self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
            return declaration_types[self.prev[0]]()
        return self.statement()


    def program(self):
        declarations = tuple()
        while self.tokens[0][0] != 'TK_EOF':
            declarations = declarations + (self.declaration(),)
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        return ('PROGRAM',) + (declarations,)


    def parse(self, tokens):
        self.tokens = tokens
        self.prev = tokens[0]
        return self.program()


    # Rule entries follow the following format:
    # prefix handler, infix handler, precedence number
    # TODO: Need to add support for compound initializers
    rule = {

            'TK_LPAR':          (group, call, Precedence.CALL),
            'TK_RPAR':          (None, None, Precedence.NONE),
            'TK_LBRACE':        (None, None, Precedence.NONE), # compound init.
            'TK_RBRACE':        (None, None, Precedence.NONE),
            'TK_DPLUS':         (pre_op, post_op, Precedence.UNARY),
            'TK_DMINUS':        (pre_op, post_op, Precedence.UNARY),
            'TK_MINUS':         (unary, binary, Precedence.TERM),
            'TK_PLUS':          (None, binary, Precedence.TERM),
            'TK_SLASH':         (None, binary, Precedence.FACTOR),
            'TK_STAR':          (unary, binary, Precedence.FACTOR),
            'TK_BANG':          (unary, None, Precedence.TERM),
            'TK_AND':           (unary, binary, Precedence.BIN_AND),
            'TK_OR':            (None, binary, Precedence.BIN_OR),
            'TK_XOR':           (None, binary, Precedence.BIN_XOR),
            'TK_NOT':           (unary, None, Precedence.UNARY),
            'TK_LSHIFT':        (None, binary, Precedence.SHIFT),
            'TK_RSHIFT':        (None, binary, Precedence.SHIFT),
            'TK_EQUAL':         (None, binary, Precedence.ASSIGNMENT),
            'TK_EQEQUAL':       (None, binary, Precedence.EQUALITY),
            'TK_GEQUAL':        (None, binary, Precedence.COMPARISON),
            'TK_LEQUAL':        (None, binary, Precedence.COMPARISON),
            'TK_GREATER':       (None, binary, Precedence.COMPARISON),
            'TK_LESSER':        (None, binary, Precedence.COMPARISON),
            'TK_QMARK':         (None, ternary, Precedence.TERNARY),
            'TK_COLON':         (None, None, Precedence.NONE),
            'TK_COMMA':         (None, None, Precedence.NONE),
            'TK_LAND':          (None, binary, Precedence.AND),
            'TK_LOR':           (None, binary, Precedence.OR),
            'TK_TYPE':          (None, None, Precedence.NONE),
            'TK_SIZEOF':        (unary, None, Precedence.UNARY),
            'TK_IDENTIFIER':    (variable, None, Precedence.PRIMARY),
            'TK_NUMBER':        (type_number, None, Precedence.PRIMARY),
            'TK_STRING':        (type_string, None, Precedence.PRIMARY),
            'TK_ENDLINE':       (None, None, Precedence.NONE),
            'TK_EOF':           (None, None, Precedence.NONE),
    }
