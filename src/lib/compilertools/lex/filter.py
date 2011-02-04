
# Certain language elements don't make sense to exclude during lexical analysis
# but are needlessly difficult to handle during parsing. A good example would be
# comments. In practice it's nice to completely specify all lexical elements of a
# language including comment tokens. Writing a grammar to accommodate all places
# where comment tokens can appear is cumbersome but you don't want your lexer to
# have any syntactic knowledge.
# 
# A simple stream filter can be placed between the lexer and parser. It will
# globally remove certain token types from the stream.


from util.pretty_printing_list import PrettyPrintingList


class Filter(object):
   """Token stream filter.

   A translator object that removes certain element types from a list.

   """

   # XXX TEST not unit tested.

   def __init__(self, ignore):
      """Construct a filter.
      
      Parameters:
         ignore - A list of token types to remove from the stream.
      
      """

      self._ignore = ignore


   def __call__(self, tokenStream):
      tokens = PrettyPrintingList()
      for token in tokenStream:
         if token.__class__ not in self._ignore:
            tokens.append(token)
      
      return (tokens, [])
