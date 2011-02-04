
from util.pretty_printing_list import PrettyPrintingList


EOFSymbol = "EOF"


class ByteScanner(object):

   def __call__(self, source):
      
      # This approach is more memory intensive but so much simpler to get right.
      characterStream = PrettyPrintingList()
      
      while True:
         # Be sure to get the position before reading the character.
         position = source.tell()
         char = source.read(1)

         if not char:
            break
         else:
            characterStream.append((char, position))
      
      characterStream.append((EOFSymbol, source.tell()))
      return (characterStream, [])
