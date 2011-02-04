"""Abstract implementation of the visitor pattern.

"""


class Visitor(object):
   """Visitor abstract base class.
   
   To implement a visitor simply subclass the visitor class and implement a 
   visit method for each item type the concrete visitor might have to handle.
   
   For example, suppose the visitor is asked to visit the tree structure:
   item1 <type 'ParentNode'>
      item2 <type 'LeftChildNode'>
      item3 <type 'RightChildNode'>
   
   Then the concrete visitor is responsible for the following:
      1) Implementing a double dispatch method eg: visitParentNode. The name is 
         simply the name of the type that must be handled appended to 'visit'.
      2) Controlling the traversal by implementing the proper actions for each 
         type that might be visited.

   The abstract class simply provides the basic double dispatch implementation 
   and default behaviour for unhandled types (raises an AttributeError).

   """
   
   def visit(self, item):
      # XXX this would be much more efficient using method dispatch decorators.
      # That's only available in newer versions of Python.
      dispatchFunc = getattr(self, "visit" + type(item).__name__, None)
      if not dispatchFunc:
         raise AttributeError, item
      else:
         return dispatchFunc(item)
