

# XXX TEST, not unit tested.

class LinkedDict(dict):
   """Supports hierarchical lookups and local writes.
   
   A LinkedDict merges the concepts of a linked list with a dictionary. 
   LinkedDict instances can be read from and written to like any mapping object: 
   http://docs.python.org/lib/typesmapping.html.
   
   New instances are created with a parent. A parent must also be a mapping 
   type, most likely it will also be a LinkedDictInstance. If the lookup for a 
   key fails the search is resumed in the parent. The parent can never be 
   modified through LinkedDict instances but their behaviour can be changed if 
   some other part of the program modifies the parent.


   XXX This implementation is just the bare essentials. Not all features, for 
   example comparison, work as expected. It would be trivial to implement all 
   Python special methods to make recursive calls to the parent - it's just a 
   matter of time.

   """

   
   def __init__(self, parent={}):
      dict.__init__(self)
      self._parent = parent


   def __getitem__(self, key):
      try:
         return dict.__getitem__(self, key)
      except:
         return self._parent[key]

   
   def get(self, key, default=None):
      return dict.get(self, key, self._parent.get(key, default))


   def localKeys(self):
      return self.keys()
