from error import SemanticError

class SymbolTable():
    def __init__(self):
        self.symbols = {
            'int':      ('int',),
            'float':    ('float',),
            'void':     ('void',)
        }


    def insert(self, name, type_info, params=None, body=None):
        if body:
            self.symbols[name] = (type_info, params, True)
        else:
            self.symbols[name] = (type_info, params, False)


    def lookup(self, name):
        return self.symbols.get(name)


class SemanticAnalyzer():

    def __init__(self):
        self.symbol_table = SymbolTable()


    def visit_program(self, prog):
        jt = {
                'DECLARE':  self.visit_declaration,
                'FUNCTION': self.visit_function
        }
        for statement in prog[-1]:
            if not statement[0] in ('DECLARE', 'FUNCTION'):
                raise SemanticError('expected declaration or function definition')
            jt[statement[0]](statement)


    def visit_declaration(self, var):
        type_info = self.symbol_table.lookup(var[1])
        if not type_info:
            self.symbol_table.insert(*var[1 : ])
        elif type_info[0] == var[2]:
            raise SemanticError('redefinition of \'{}\''.format(var[1]))


    def visit_block(self, block):
        for s in block[-1]:
            self.visit_declaration(s)


    def visit_function(self, func):
        type_info = self.symbol_table.lookup(func[1])

        if not type_info:
            self.symbol_table.insert(*func[1 : ])
            if func[-1]:
                    self.visit_block(func[-1])
        elif type_info[-1] and func[-1]:
            raise SemanticError('redefinition of \'{}\''.format(func[1]))
        elif type_info[0] == func[2]:
            self.symbol_table.insert(*func[1 : ])
        else:
            raise SemanticError('redefinition of \'{}\''.format(func[1]))


    def visit_return(self, statement):
        if statement[-1]:
            pass


    def analyze(self, ast=tuple()):
        self.visit_program(ast)

        return self.symbol_table.symbols
