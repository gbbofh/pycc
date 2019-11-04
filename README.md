# PyCC
## A simple, work in progress, C compiler
### Why?
This is being written as a project to prepare for my last class as an
undegraduate -- compiler writing. I don't expect this to fully work, and right
now it doesn't, I just don't want to be completely lost when my class starts.

### To do
There is a lot left to do in this project, and I will likely be working on it
for some time. It could be worth while to refactor the parser and lexer to work
on classes for AST nodes and tokens respectively, but as of right now, and for
the indefinite future, I will be sticking with building up nested tuples/lists
as it works just as well considering that this is a prototype project. The
semantic analysis portion needs reworked, and it is very much in its infancy
right now -- it is completely incapable of handling scope at this time, but this
should be fixed in the coming days.

Code generation is not implemented yet, but should be coming soon-ish.

### Status

Currently the parser and semantic analyzer are capable of handling relatively
complex expressions such as:
        int get\_bits(float f)
                return *(int*)&f;
        }

Structures are not currently fully implemented, but are a work in progress.
