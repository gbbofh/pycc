import re

from error import PreprocessError

class Preprocessor():
    symbols = {
    }

    def __init__(self):
        pass

    def process(self, lines):
        new_lines = []
        for line in lines:
            re.sub('//.+$', '', line)
            m = re.search('#define', line)
            if m:
                ident = re.search('[A-Za-z_][A-Za-z0-9_]*', line[m.end() : ])
                val = line[m.end() + ident.end() : ]
                self.symbols[ident.group().strip()] = val.strip()
                line = line[0 : m.start()]
            m = re.search('#include', line)
            if m:
                path = line[m.end() : ].strip()
                with open(path.strip('"')) as fp:
                    tl = [x.strip() for x in fp.readlines()]
                    tl = self.process(tl)
                    new_lines += tl
                line = line[0 : m.start()]
            for i in self.symbols:
                m = re.search(i, line)
                if m:
                    line = re.sub(m.re, self.symbols[i], line) 
            if line:
                new_lines.append(line)
        return new_lines
