"""The CPLR intermediate representation.

CPLR-IR is a tree language that models an abstract instruction set architecture.
Since it is a tree language, any expression in the language can have no
ambiguity.

The analysis phase for a language produces CPLR-IR while the synthesis phase
consumes CPLR-IR and generates instructions for a suitable architecture.


XXX Function decls.
XXX Function calls
XXX C function calls
XXX IO

"""


class IRNode(object):
   """IR base type.
   
   """

   def __init__(self, children):
      self.__children = children


# The 2 abstract base classes. 
class Expression(IRNode):
   pass

class Statement(IRNode):
   pass


class NullStatement(Statement):
   """A statement with no side effects
   
   """
   
   def __init__(self):
      Statement.__init__(self, None)


class CCall(Expression):
   pass