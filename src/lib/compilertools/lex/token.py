""" XXX docs

"""


# All lexical tokens will derive from the Token class.

class Token(object):
   """The base class for tokens.

   The startIndex and endIndex define the position in the source such that 
   source.seek(0)
   source.seek(startIndex)
   tokenCharacters = source.read(endIndex - startIndex)

   """

   def __init__(self, startIndex, endIndex, lexeme):
      self.__start = startIndex
      self.__end = endIndex
      

      
   def endIndex(self):
      return self.__end


   def startIndex(self):
      return self.__start


   def __str__(self):
      return "<%s: [%d : %d]>" % \
             (self.__class__.__name__, self.__start, self.__end)


# Not all lexical elements actually occur as byte sequences in the source.
# Those tokens are represented by subclasses of a VirtualToken.

class VirtualToken(Token):
   """Represents a syntactic element that doesn't appear in the source.
   
   Inserting virtual tokens in to the token stream is useful to set markers for 
   a parse to interpret at a later stage.

   """
   
   def __init__(self):
      Token.__init__(self, -1, -1, "")
   
   def __str__(self):
      return "%s (virtual)" % Token.__str__(self)


# The 2 prime examples of VirtualTokens are the beginning of file and end of
# file markers.

class BOF(VirtualToken):
   pass

class EOF(VirtualToken):
   pass


# There are also many tokens useful to multiple languages.

class Identifier(Token):
   
   def __init__(self, startIndex, endIndex, lexeme):
      Token.__init__(self, startIndex, endIndex, lexeme)
      self.name = lexeme

class ReservedWord(Token): pass


# Even though comments have no semantic difference to most programs they do to
# some (e.g.: Python). Furthermore a lexical analyzer shouldn't be concerned
# with that fact. It also makes the lexer more testable if comment tokens are
# included in the token stream.

class Comment(Token): pass

class IntegerLiteral(Token): pass
class FloatLiteral(Token): pass
class StringLiteral(Token): pass
class CharacterLiteral(Token): pass

