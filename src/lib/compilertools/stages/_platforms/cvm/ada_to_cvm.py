"""A quick and dirty ada AST to C macro code.

"""

from util.visitor import Visitor

from compilertools.stages.obj import Obj

class AdaToCVM(Visitor):


   def __call__(self, abstractSyntaxTree):
      fragment = self.visit(abstractSyntaxTree)
      return (Obj(abstractSyntaxTree.namespace,
                  abstractSyntaxTree.visibleSyms,
                  fragment),
              [])


################################################################################

   def visitCompilation(self, compilation):
      return self.visit(compilation.children["subprogramBody"])

   def visitSubprogramBody(self, subprogramBody):
      children = subprogramBody.children
      
      return r"""
      void %s()
      {
       %s
       %s
      };""" % (self.visit(children["subprogramSpec"]),
               self.visit(children["optSubprogramDeclPart"]),
               self.visit(children["statements"]))

   def visitSubprogramSpec(self, subprogramSpec):
      localKeys = subprogramSpec.visibleSyms.localKeys()
      assert len(localKeys) == 1
      return localKeys[0]

   def visitOptSubprogramDeclPart(self, optSubprogramDeclPart):
      return ""

   def visitStatements(self, statements):
      # XXX do a proper iteration
      return self.visit(statements.children["printStmt"])

   def visitPrintStmt(self, printStmt):
      # XXX handle more than just strings here.
      # XXX registerfy this
      printType = r"%s"
      return '''
      printf("%s", "%s");
      ''' % (printType, self.visit(printStmt.children["stringLit"]))

   def visitStringLit(self, stringLit):
      return stringLit.value