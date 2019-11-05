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
            re.sub('//.*$', '', line)
            m = re.search('(#define)', line)
            if m:
                ident = re.search('[A-Za-z_][A-Za-z_0-9]*', line[m.end() : ])
                val = re.search('.*', line[ident.end() + m.end() : ])
                if val:
                    line = line[0 : m.start()] + line[m.end() + val.end() + ident.end():]
                    self.symbols[ident.group()] = val.group()
                else:
                    line = line[0 : m.start()] + line[m.end() + ident.end():]
                    self.symbols[ident.group()] = ''
            for i in self.symbols:
                m = re.search(i, line)
                if m:
                    re.sub(m.re, self.symbols[i], line) 
            new_lines.append(line)
        return new_lines
