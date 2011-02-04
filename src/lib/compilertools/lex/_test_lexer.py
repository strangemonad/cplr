import unittest

from lang.reg import epsilon_nfa

from compilertools import scanner

import lexer
import token


class LongestMatchTestCase(unittest.TestCase):

   # XXX TEST this is really just a smoke test.

   def testNullSyntaxDefinition(self):
      self.assertRaises(AssertionError, lexer.LongestMatchLexer,\
                        None)

   def testEmptySyntaxDefinition(self):
      lex = lexer.LongestMatchLexer([])
      (tokenStream, issues) = lex([("a", 0), ("b", 1)])
      self.assertEqual(tokenStream, None)
      self.assertEqual(len(issues), 1)

      self.assertEqual(issues[0].startIndex(), 0)
      self.assertEqual(issues[0].endIndex(), 0)

   def testTrivialSyntaxDefinition(self):
      syntaxDef = [(epsilon_nfa.symbol("a").toDFA(), token.Token),
                   (epsilon_nfa.symbol(scanner.EOFSymbol).toDFA(), None)]
      lex = lexer.LongestMatchLexer(syntaxDef)
      (tokenStream, issues) = lex([("a", 0), (scanner.EOFSymbol, 1)])
      self.assertEqual(len(tokenStream), 3)
      self.assertFalse(issues)

      self.assertEqual(tokenStream[0].__class__, token.BOF)
      self.assertEqual(tokenStream[0].startIndex(), -1)
      self.assertEqual(tokenStream[0].endIndex(), -1)
      
      self.assertEqual(tokenStream[1].__class__, token.Token)
      self.assertEqual(tokenStream[1].startIndex(), 0)
      self.assertEqual(tokenStream[1].endIndex(), 1)
      
      self.assertEqual(tokenStream[2].__class__, token.EOF)
      self.assertEqual(tokenStream[2].startIndex(), -1)
      self.assertEqual(tokenStream[2].endIndex(), -1)
      
      (tokenStream, issues) = lex([("b", 0), (scanner.EOFSymbol, 1)])
      self.assertEqual(tokenStream, None)
      self.assertEqual(len(issues), 1)

      self.assertEqual(issues[0].startIndex(), 0)
      self.assertEqual(issues[0].endIndex(), 0)



if __name__ == '__main__':
   unittest.main()
