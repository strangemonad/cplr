
import unittest

import analysis
from compilertools import environment
from compilertools import error


class MakeAnayliserTestCase(unittest.TestCase):

   def testNullEnvironment(self):
      self.assertRaises(AttributeError, analysis.makeAnalyzer, None)

   def testUnsupportedDialect(self):
      self.assertRaises(analysis.UnsupportedDialectException,
                        analysis.makeAnalyzer, environment.empty())

      self.assertRaises(analysis.UnsupportedDialectException,
                        analysis.makeAnalyzer,
                        {environment.DIALECT : "fhdskaj"})

   def testAdaDialect(self):
      env = environment.empty()
      env[environment.DIALECT] = "ada"
      analyzer = analysis.makeAnalyzer(env)
      self.assert_(analyzer)
      # XXX TEST: that the analyzer is a valid translator object.


class UnsupportedDialectExceptionTestCase(unittest.TestCase):

   def testType(self):
      try:
         raise analysis.UnsupportedDialectException, "some-dialect"
      except error.CompilerException:
         pass
      except:
         self.fail("UnsupportedDialectException should be a CompilerException.")
      else:
         self.fail("Unable to raise an UnsupportedDialectException.")
   
   def testCreateNoParameters(self):
      try:
         raise analysis.UnsupportedDialectException
      except TypeError:
         pass
      except:
         self.fail("UnsupportedDialectException() should fail with no params.")
      else:
         self.fail("UnsupportedDialectException() should fail with no params.")

   def testRandomDialectName(self):
      dialectName = "some-dialect"
      e = analysis.UnsupportedDialectException(dialectName)
      self.assert_(not str(e).startswith(dialectName))


if __name__ == '__main__':
   unittest.main()
