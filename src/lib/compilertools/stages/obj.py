"""A basic information represented by an object file.

"""

class Obj(object):

   def __init__(self, namespace, symbols, fragment):
      self.namespace = namespace
      self.symbols = symbols
      self.fragment = fragment
   
   def __str__(self):
      return "%s\n%s" % (self.symbols, self.fragment)
