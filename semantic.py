from error import SemanticError

class SymbolTable():
    def __init__(self):
        self.symbols = {
            'int':      ('int',),
            'float':    ('float',),
            'void':     ('void',)
        }


    def insert(self, name, *args):
        self.symbols[name] = args


    def lookup(self, name):
        return self.symbols.get(name)


class SemanticAnalyzer():

    def __init__(self):
        self.globals = SymbolTable()


    def visit_program(self, prog):
        jt = {
                'DECLARE':  self.visit_declaration,
                'FUNCTION': self.visit_function,
                'STRUCT': lambda x: False
        }
        for statement in prog[-1]:
            if not statement[0] in jt.keys():
                raise SemanticError('expected declaration or function definition')
            jt[statement[0]](statement)


    def visit_declaration(self, var):
        type_info = self.globals.lookup(var[1])
        if not type_info:
            self.globals.insert(var[1], var[2:])
            if var[2] == 'void':
                raise SemanticError('cannot declare variable of type void')
        elif type_info[0] == var[2]:
            raise SemanticError('redefinition of {}'.format(var[1]))


    def visit_assignment(self, var):
        type_info = self.globals.lookup(var[1][1])
        if not type_info:
            raise SemanticError('undefined variable {}'.format(var[1]))
        self.visit_expr(var[-1])


    def visit_variable(self, var):
        type_info = self.globals.lookup(var[1])
        if not type_info:
            raise SemanticError('undefined variable {}'.format(var[1]))


    def visit_unary(self, expr):
        self.visit_expr(expr[1 : ])


    def visit_binary(self, expr):
        for operand in expr[1 : ]:
            self.visit_expr(expr)


    def visit_expr(self, expr):
        jt = {
                'ADD': self.visit_binary,
                'SUB': self.visit_binary,
                'MULT': self.visit_binary,
                'DIV': self.visit_binary,
                'BITWISE_AND': self.visit_binary,
                'BITWISE_OR': self.visit_binary,
                'BITWISE_XOR': self.visit_binary,
                'LEFTSHIFT': self.visit_binary,
                'RIGHTSHIFT': self.visit_binary,
                'ASSIGN': self.visit_binary,
                'EQUAL': self.visit_binary,
                'GEQUAL': self.visit_binary,
                'LEQUAL': self.visit_binary,
                'NEQUAL': self.visit_binary,
                'GREATER': self.visit_binary,
                'LESSER': self.visit_binary,
                'LOGICAL_AND': self.visit_binary,
                'LOGICAL_OR': self.visit_binary,
                'NEGATE': self.visit_unary,
                'NEGATE': self.visit_unary,
                'BANG': self.visit_unary,
                'BITWISE_NOT': self.visit_unary,
                'REFERENCE': self.visit_unary,
                'DEREFERENCE': self.visit_unary,
                'SIZEOF': self.visit_unary
        }
        jt.get(expr[0], lambda e: None)(expr)


    def visit_while(self, stmt):
        pass


    def visit_do_while(self, stmt):
        pass


    def visit_if(self, stmt):
        pass


    def visit_return(self, stmt):
        pass


    def visit_block(self, block):
        jt = {
                'CALL':     self.visit_call,
                'DECLARE':  self.visit_declaration,
                'ASSIGN':   self.visit_assignment,
                'IF':       self.visit_if,
                'WHILE':    self.visit_while,
                'DO_WHILE': self.visit_do_while,
                'RETURN':   self.visit_return
        }
        for s in block[-1]:
            jt.get(s[0], lambda s: None)(s)


    def visit_function(self, func):
        type_info = self.globals.lookup(func[1])

        if not type_info:
            self.globals.insert(func[1], func[0:-1], True if func[-1] else False)
            if func[-1]:
                    self.visit_block(func[-1])
        elif type_info[-1] and func[-1]:
            raise SemanticError('redefinition of {}'.format(func[1]))
        elif type_info[0] == func[2]:
            self.globals.insert(func[1], func[0:-1], True if func[-1] else False)
            self.visit_block(func[-1])
        else:
            raise SemanticError('redefinition of {}'.format(func[1]))


    def visit_call(self, func):
        type_info = self.globals.lookup(func[1])
        if not type_info:
            raise SemanticError('undefined reference to {}'.format(func[1]))
        elif len(type_info[1]) > len(func[2]):
            raise SemanticError('too few arguments to {}'.format(func[1]))
        elif len(type_info[1]) < len(func[2]):
            raise SemanticError('too many arguments to {}'.format(func[1]))


    def analyze(self, ast=tuple()):
        self.visit_program(ast)

        return self.globals.symbols
