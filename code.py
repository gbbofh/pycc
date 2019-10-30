class CodeGenerator():

    def __init__(self):
        self.decls = dict()


    def generate(self, ast):

        top_level = ast[1 : ]
        for st in top_level:
            if 'FUNCTION' in st:
                decl[st[1]] = (st[2], st[3], st[4])
            elif 'DECLARE' in st:
                decl[st[1]] = (st[2], st[3])
            elif 'VARIABLE' in st:
                if st not in decl:
                    raise Exception('bad.')
