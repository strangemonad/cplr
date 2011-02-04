""" The set of parse tree nodes that might occur in a derivation of a syntactically valid Ada compilation.

"""

from compilertools.parse.tree import Node, NotImplementedNode, _extents
      

class Compilation(Node):
   def __init__(self, subprogramBody_):
      Node.__init__(self, *_extents(subprogramBody_)) # XXX this will change.

      self.children["subprogramBody"] = subprogramBody_
      self.types = {}


class CompilationUnit(Node): pass
class ContextClause(Node): pass
class LibraryUnit(Node): pass

class PackageBody(Node): pass
class PackageDecl(Node): pass

class SubprogramBody(Node):
   def __init__(self,
                subprogramSpec_, is_, optSubprogramDeclPart_,
                begin_, statements_, end_, optDesignator_, semiColon_):
      Node.__init__(self, *_extents(subprogramSpec_, semiColon_))

      # XXX simplify the optSubprogramDeclPart in the AST
      # remove it from the visitors.

      self.children["subprogramSpec"] = subprogramSpec_
      self.children["optSubprogramDeclPart"] = optSubprogramDeclPart_
      self.children["statements"] = statements_
      self.children["optDesignator"] = optDesignator_


class SubprogramDecl(Node): pass
class SubprogramSpec(Node):
   def __init__(self, procedure_, identifier_):
      Node.__init__(self, *_extents(procedure_, identifier_))

      self.children["identifier"] = identifier_

class OptSubprogramDeclPart(Node): pass      

class Statements(Node):
   def __init__(self, printStmt_):
      # XXX this needs to be fixed to take a generic list of statements.
      Node.__init__(self, *_extents(printStmt_))

      self.children["printStmt"] = printStmt_


class Designator(Node):
   def __init__(self, identifier_=None, operatorSymbol_=None):
      assert identifier_ or operatorSymbol_

      Node.__init__(self, *_extents(identifier_ or operatorSymbol_))

      # XXX this can possibly be simplified.
      self.children["identifier"] = identifier_
      self.children["operatorSymbol"] = operatorSymbol_

class OptDesignator(Node):
   def __init__(self, designator_=None):
      Node.__init__(self, *_extents(designator_))

      self.children["designator"] = designator_

class OperatorSymbol(Node): pass

class Statement(Node): pass


# Hacky additions:

class PrintStmt(Statement):
   def __init__(self, putLine_, parenL_, stringLit_, parenR_, semiColon_):
      Node.__init__(self, *_extents(putLine_, semiColon_))

      # XXX need to handle more than just string literals.
      self.children["stringLit"] = stringLit_
