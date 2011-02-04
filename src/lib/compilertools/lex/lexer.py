
import copy

from util.pretty_printing_list import PrettyPrintingList

from lang.reg.dfa import UndefinedTransitionError

from compilertools.error import CompilationError

import token


class UnexpectedSymbolError(CompilationError):
   """An error in the syntax.
   
   """

   def __str__(self):
      # XXX come back and figure out printing of erors.
      return "UNEXPECTED SYMBOL %s" % CompilationError.__str__(self)


class LongestMatchLexer(object):


   def __init__(self, syntaxDefinition):
      """ XXX Docs
      
      Parameters:
         syntaxDefinition - A non-null, possibly empty array of (dfa, tokenType) 
                            pairs.

      """

      assert syntaxDefinition != None

      
      # It makes more sense when defining to make higher priority elements come
      # first in the list to break ties. The algorithm used internally though
      # returns a token of the last matching DFA in the list.
      self.__syntaxDefinition = list(syntaxDefinition)
      self.__syntaxDefinition.reverse()


   def __call__(self, charStream):
      tokenStream = PrettyPrintingList()
      issues = []

      # This offset can be done away with and instead iterate over the stream.
      offset = 0

      while offset < len(charStream):
         (numCharsMatched, tokenType) = self._longestMatch(charStream[offset:])

         if numCharsMatched:
            if tokenType != None:
               # XXX should this be an ASSERT tokenType?
               startIndex = charStream[offset][1]
               try:
                  endIndex = charStream[offset + numCharsMatched][1]
                  matched = charStream[offset : offset + numCharsMatched]
               except IndexError:
                  # It the file doesn't end with a newline.
                  endIndex = charStream[offset + numCharsMatched -1][1]
                  matched = charStream[offset : offset + numCharsMatched -1]


               # XXX this is kind of ugly. Only certain token types need to 
               # hold on the the original character information for their 
               # values. In some cases this even involved re-scanning (eg: 
               # numeric literals).
               lexeme = "".join([item[0] for item in matched])
               nextTok = tokenType(startIndex, endIndex, lexeme)

               tokenStream.append(nextTok)
            offset += numCharsMatched
         else:
            # XXX Lots more smarts here in error recovery.
            tokenStream = None
            issues.append(UnexpectedSymbolError(charStream[offset][1],\
                                                charStream[offset][1]))
            break

      # XXX jsut hack in the insertion of BOF and EOF for now
      if tokenStream != None:
         tokenStream.insert(0, token.BOF())
         tokenStream.append(token.EOF())
      return (tokenStream, issues)


   def _longestMatch(self, remainingCharStream):
      
      # XXX TODO, this iteration scheme will be really slow. Move to a scheme 
      # where all of the DFAs are combined into one to make use of parallelism.

      charsMatched = 0
      matchedTokenType = None
      
      for (dfa, tokenType) in self.__syntaxDefinition:
         dfa.reset()

      # This is only needed because we don't have a unified DFA transducer.
      someDFACanMakeProgress = True
      offset = 0
      while someDFACanMakeProgress and (offset < len(remainingCharStream)):
         someDFACanMakeProgress = False

         for (dfa, tokenType) in self.__syntaxDefinition:
            try:
               dfa.run(remainingCharStream[offset][0])
            except UndefinedTransitionError:
               pass
            else:
               someDFACanMakeProgress = True
               
               if dfa.accepts():
                  charsMatched = offset + 1
                  matchedTokenType = tokenType
               
         offset += 1

      return (charsMatched, matchedTokenType)
