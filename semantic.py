from error import SemanticError


class SymbolTable():
    def __init__(self, outer=None):
        self.symbols = {
            'int':      ('int',),
            'float':    ('float',),
            'void':     ('void',)
        }

        self.outer = outer


    def insert(self, name, *args):
        self.symbols[name] = args[0]


    def lookup(self, name, check_outer=True):
        sym = self.symbols.get(name)
        if not sym and self.outer and check_outer:
            return self.outer.lookup(name)
        return sym


    def clear(self):
        self.symbols.clear()


class SemanticAnalyzer():

    def __init__(self):
        self.globals = SymbolTable()
        self.current = self.globals
        self.types = SymbolTable() # Each struct/union/enum gets its own table
        self.labels = SymbolTable()


    def visit_program(self, prog):
        jt = {
                'DECLARE':  self.visit_global_declaration,
                'DECL_FUNC': self.visit_function_declaration,
                'FUNCTION': self.visit_function,
                'STRUCT': lambda x: False
        }
        for statement in prog[-1]:
            if not statement[0] in jt.keys():
                raise SemanticError('expected declaration')
            jt[statement[0]](statement)


    def constant(self, expr):
        pass


    # TODO: Check if global declarations evaluate to constant expressions
    def visit_global_declaration(self, var):
        self.visit_declaration(var)
        self.constant(var[2:])


    def visit_declaration(self, var):
        type_info = self.current.lookup(var[1], check_outer=False)
        if not type_info:
            self.current.insert(var[1], var[2:])
            if var[2] == 'void':
                raise SemanticError('identifier ' + var[1] + ' cannot be void')
        elif type_info[0] == var[2]:
            raise SemanticError('redefinition of {}'.format(var[1]))
        elif type_info[0] != var[1]:
            raise SemanticError('conflicting types for {}'.format(var[1]))

        if var[-1]:
            self.visit_expr(var[-1])


    def visit_function_declaration(self, var):
        type_info = self.current.lookup(var[1], check_outer=False)
        if not type_info:
            self.current.insert(var[1], var[2:])
        elif type_info[0] == var[2]:
            raise SemanticError('redefinition of {}'.format(var[1]))
        elif type_info[0] != var[1]:
            raise SemanticError('conflicting types for {}'.format(var[1]))


    def visit_assignment(self, var):
        type_info = self.current.lookup(var[1][1])
        if not type_info:
            raise SemanticError('undefined variable {}'.format(var[1]))
        self.visit_expr(var[-1])


    def visit_variable(self, var):
        type_info = self.current.lookup(var[1])
        if not type_info:
            raise SemanticError('undefined variable {}'.format(var[1]))


    def visit_unary(self, expr):
        self.visit_expr(expr[-1])


    def visit_binary(self, expr):
        for operand in expr[1 : ]:
            self.visit_expr(operand)


    def visit_expr(self, expr):
        jt = {
                'CALL': self.visit_call,
                'ADD': self.visit_binary,
                'SUB': self.visit_binary,
                'MULT': self.visit_binary,
                'DIV': self.visit_binary,
                'BITWISE_AND': self.visit_binary,
                'BITWISE_OR': self.visit_binary,
                'BITWISE_XOR': self.visit_binary,
                'LEFTSHIFT': self.visit_binary,
                'RIGHTSHIFT': self.visit_binary,
                'ASSIGN': self.visit_assignment,
                'EQUAL': self.visit_binary,
                'GEQUAL': self.visit_binary,
                'LEQUAL': self.visit_binary,
                'NEQUAL': self.visit_binary,
                'GREATER': self.visit_binary,
                'LESSER': self.visit_binary,
                'LOGICAL_AND': self.visit_binary,
                'LOGICAL_OR': self.visit_binary,
                'NEGATE': self.visit_unary,
                'BANG': self.visit_unary,
                'BITWISE_NOT': self.visit_unary,
                'REFERENCE': self.visit_unary,
                'DEREFERENCE': self.visit_unary,
                'SIZEOF': self.visit_unary,
                'VARIABLE': self.visit_variable,
                'PREINCREMENT': self.visit_unary,
                'POSTINCREMENT': self.visit_unary
        }
        jt.get(expr[0], lambda e: None)(expr)


    def visit_while(self, stmt):
        self.visit_expr(stmt[1])
        self.visit_statement(stmt[2])


    def visit_do_while(self, stmt):
        self.visit_statement(stmt[1])
        self.visit_expr(stmt[2])


    def visit_if(self, stmt):
        self.visit_expr(stmt[1])
        self.visit_statement(stmt[2])
        if stmt[3]:
            self.visit_statement(stmt[3][0])


    def visit_return(self, stmt):
        self.visit_expr(stmt[1])


    def visit_block(self, block):
        sym = SymbolTable(self.current)
        self.current = sym

        for s in block[-1]:
            self.visit_statement(s)

        self.current = self.current.outer


    def visit_statement(self, stmt):
        jt = {
                'DECLARE':  self.visit_declaration,
                'ASSIGN':   self.visit_assignment,
                'IF':       self.visit_if,
                'WHILE':    self.visit_while,
                'DO_WHILE': self.visit_do_while,
                'RETURN':   self.visit_return,
                'BLOCK':    self.visit_block,
                'EMPTY':    lambda s: None
        }
        jt.get(stmt[0], self.visit_expr)(stmt)


    def visit_function(self, func):
        type_info = self.current.lookup(func[1])

        if not type_info:
            self.current.insert(func[1], func[2 : -1], True)
        elif type_info[-1]:
            raise SemanticError('redefinition of {}'.format(func[1]))
        elif type_info[0] == func[2]:
            self.current.insert(func[1], func[2 : -1])
            self.visit_block(func[-1])
        else:
            raise SemanticError('redefinition of {}'.format(func[1]))

        sym = SymbolTable(self.current)
        self.current = sym

        for p in func[3]:
            type_info = self.current.lookup(p[1])
            if not type_info:
                self.current.insert(p[1], p[2])
            else:
                raise SemanticError('redefininition of parameter ' + p[1])

        self.visit_block(func[-1])

        self.current = self.current.outer


    def visit_call(self, func):
        type_info = self.current.lookup(func[1])
        if not type_info:
            raise SemanticError('undefined reference to {}'.format(func[1]))
        elif len(type_info[1]) > len(func[2]):
            raise SemanticError('too few arguments to {}'.format(func[1]))
        elif len(type_info[1]) < len(func[2]):
            raise SemanticError('too many arguments to {}'.format(func[1]))

        for p in func[2]:
            type_info = self.current.lookup(p[1])
            if not type_info:
                raise SemanticError('undefined reference to ' + p[1])


    def analyze(self, ast=tuple()):
        self.globals.clear()
        self.current = self.globals
        self.visit_program(ast)

        return self.current.symbols
