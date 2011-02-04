
from util.linked_dict import LinkedDict

from compilertools.ast_visitor import ASTVisitor
from compilertools.error import CompilationError


class UndefinedSymbolError(CompilationError):

   def __str__(self):
      return "UNDEFINED SYMBOL %s" % CompilationError.__str__(self)
      

class SymbolCollector(ASTVisitor):
   """Collect all symbols with appropriate scoping.
   
   The symbol collector visitor will just return the AST annotated with symbol 
   information.
   
   The pattern for each dispatch method is roughly the same
      - Collect all symbols visible at a particular level.
      - Recurse over the child nodes of interest.

   """

   def visitCompilation(self, compilation):
      compilation.visibleSyms = LinkedDict()
      compilation.namespace = "_"
      
      # XXX this will change to be more generic.
      subprogramBody = compilation.children["subprogramBody"]
      subprogramBody.visibleSyms = compilation.visibleSyms
      subprogramBody.namespace = compilation.namespace 
      self.visit(subprogramBody)


   def visitSubprogramBody(self, subprogramBody):
      subprogramSpec = subprogramBody.children["subprogramSpec"]
      subprogramSpec.visibleSyms = subprogramBody.visibleSyms
      subprogramSpec.namespace = subprogramBody.namespace
      self.visit(subprogramSpec)
      # XXX TODO handle checking optDesignator
      # XXX still need to handle nested body content.

   def visitSubprogramSpec(self, subprogramSpec):
      symbolName = subprogramSpec.namespace +\
                   subprogramSpec.children["identifier"].name
      subprogramSpec.visibleSyms[symbolName] = None
