
from util.visitor import Visitor

from compilertools.error import CompilationError


class UnsupportedLanguageFeatureError(CompilationError):

   def __init__(self, startIndex, endIndex, featureName):
      CompilationError.__init__(self, startIndex, endIndex)
      self.__featureName = featureName
      
   def __str__(self):
      return "'%s' - UNSUPPORTED FEATURE %s" % \
             (self.__featureName, CompilationError.__str__(self))


class ASTVisitor(Visitor):
   """Abstract implementation of a visitor for abstract syntax trees.
   
   Specializes the generic Visitor to respond more appropriately to 
   unimplemented dispatch methods.
   
   Behaves like a translator object.
   
   """
   
   def __call__(self, abstractSyntaxTree):
      self._issues = []
      try:
         self.visit(abstractSyntaxTree)
      except AttributeError, e:
         # XXX TODO - continue beyond 1 fatal error.
         node = e.args[0]
         nodeName = type(node).__name__
         self._issues.append(UnsupportedLanguageFeatureError(node.startIndex(), 
                                                             node.endIndex(),
                                                             nodeName))

      return (abstractSyntaxTree, self._issues)
