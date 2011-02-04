
# The base type for all parse tree nodes. Node itself is a childless,

class Node(object):

   def __init__(self, startIndex=-1, endIndex=-1):
      # XXX this part is very similar to the Token attributes. Maybe they should
      # have a common base class.
      self.__start = startIndex
      self.__end = endIndex

      self.children = {}
      self.visibleSyms = None
      self.namespace = ""


   def endIndex(self):
      return self.__end


   def startIndex(self):
      return self.__start


   def __str__(self):
      return type(self).__name__


class NotImplementedNode(Node):

   def __init__(self, *args):
      """Use this node type in the grammar as it's temporarily being built.
      
      If ever the parser tries to reduce a rule with this node type in the 
      production a NotImplemented assertion will be raised
      
      """
      
      from util import asserts
      asserts.NotImplemented()


def _extents(first, last=None):
   return (first.startIndex(),
           last and last.endIndex() or first.endIndex())