from enum import IntEnum
from error import ParseError

class Precedence(IntEnum):
    NONE =          0
    ASSIGNMENT =    1
    TERNARY =       2
    OR =            3
    AND =           4
    EQUALITY =      5
    COMPARISON =    6
    TERM =          7
    FACTOR =        8
    UNARY =         9
    CALL =          10
    PRIMARY =       11

class Parser():


    def __init__(self, tokens):
        self.tokens = tokens
        self.prev = tokens[0]


    # def type_int(self):
    #     i = int(self.prev[1], 0)
    #     return ('INTEGER', i)


    # def type_float(self):
    #     f = float(self.prev[1])
    #     return ('FLOAT', f)


    def type_number(self):
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
        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ] # RPAR
        return params


    def call(self, left):
        args = self.call_args()
        left = (left[1])
        return ('CALL', left, args)


    def unary(self):
        unary_ops = {
                'TK_MINUS': 'NEGATE',
                'TK_BANG': 'NOT'
        }
        op = self.prev[0]
        expr = self.parse_precedence(Precedence.UNARY)
        return (unary_ops[op], expr)


    def binary(self, left):
        binary_ops = {
                'TK_PLUS':      'ADD',
                'TK_MINUS':     'SUB',
                'TK_STAR':      'MULT',
                'TK_SLASH':     'DIV',

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


    def statement(self):
        statement_types = {
                'TK_LBRACE': self.block_statement,
                'TK_RETURN': self.return_statement,
                'TK_ENDLINE': lambda: ('EMPTY',)
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

        # if type_info == 'void':
        #     line, col = self.tokens[0][2], self.tokens[0][3]
        #     raise ParseError('variable cannot be declared void', line, col)

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
        if len(params) == 0:
            params = None
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
            return ('DECLARE', name, type_info, params)

        return ('FUNCTION', name, type_info, params, body)


    def function_variable_decl(self):
        expr = None
        type_info = self.prev[1]

        # if self.tokens[0][0] == 'TK_STAR':
        #     self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        #     type_info += '_PTR'

        if not self.tokens[0][0] == 'TK_IDENTIFIER':
            line, col = self.tokens[0][2], self.tokens[0][3]
            raise ParseError('expected identifier name', line, col)

        self.prev, self.tokens = self.tokens[0], self.tokens[1 : ]
        name = self.prev

        if self.tokens[0][0] == 'TK_LPAR':
            return self.function_decl(type_info)

        return self.variable_decl(type_info)

        # raise ParseError('expected function or variable declaration')


    def declaration(self):
        decl = None
        declaration_types = {
                'TK_TYPE':  self.function_variable_decl
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


    # Rule entries follow the following format:
    # unary handler, infix handler, precedence number
    rule = {

            'TK_LPAR':          (group, call, Precedence.CALL),
            'TK_RPAR':          (None, None, Precedence.NONE),
            'TK_LBRACE':        (None, None, Precedence.NONE),
            'TK_RBRACE':        (None, None, Precedence.NONE),
            'TK_MINUS':         (unary, binary, Precedence.TERM),
            'TK_PLUS':          (None, binary, Precedence.TERM),
            'TK_SLASH':         (None, binary, Precedence.FACTOR),
            'TK_STAR':          (None, binary, Precedence.FACTOR),
            'TK_BANG':          (unary, None, Precedence.TERM),
            'TK_EQUAL':         (None, binary, Precedence.NONE),
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
            'TK_IDENTIFIER':    (variable, None, Precedence.PRIMARY),
            #'TK_FLOAT':         (type_float, None, Precedence.PRIMARY),
            #'TK_INTEGER':       (type_int, None, Precedence.PRIMARY),
            'TK_NUMBER':        (type_number, None, Precedence.PRIMARY),
            'TK_STRING':        (type_string, None, Precedence.PRIMARY),
            'TK_ENDLINE':       (None, None, Precedence.NONE),
            'TK_EOF':           (None, None, Precedence.NONE),
    }
