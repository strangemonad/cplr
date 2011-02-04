"""Implementation of CPLR-IR to CVM code generation.


"""

from util.visitor import Visitor


class Generator(Visitor):


   def visitNullStatement(self, item):
      return ""