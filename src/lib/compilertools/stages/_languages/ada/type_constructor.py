
from compilertools.ast_visitor import ASTVisitor
from compilertools.error import CompilationError


class TypeRedefinitionError(CompilationError):

   def __init__(self, startIndex, endIndex, typeName):
      CompilationError.__init__(self, startIndex, endIndex)
      self.__typeName = typeName
      
   def __str__(self):
      return "'%s' - PREVIOUSLY DEFINED TYPE %s" % \
             (self.__featureName, CompilationError.__str__(self))


class TypeConstructor(ASTVisitor):
   """Create a representation for all types.
   
   Traverse the AST and collect a map from type name to type construction. The 
   root node of the AST will be annotated with the map.
   
   """

   def _collectChildTypes(self, node):
      # Maps type names -> type construction.
      typeDefs = {}

      for child in getattr(node, "children", {}).values():

         childTypeDefs = self.visit(child)
         for typeName, typeCtor in childTypeDefs.items():
            if typeName in typeDefs:
               error = TypeRedefinitionError(child.startIndex(),
                                             child.endIndex(),
                                             typeName)
               self._issues.append(error)
            else:
               typeDefs[typeName] = typeCtor
      return typeDefs


   def visit(self, item):
      try:
         ASTVisitor.visit(self, item)
      except AttributeError:
         try:
            return self._collectChildTypes(item)
         except AttributeError, e:
            print "Something went horribly wrong. Stopping the error here to " \
                  "prevent a stack unwinding cascade."
            print e


   def visitCompilation(self, compilation):
      compilation.types = self._collectChildTypes(compilation)
