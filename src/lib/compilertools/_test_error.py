import unittest

import error

class CompilerExceptionTestCase(unittest.TestCase):


   def testNoParams(self):
      try:
         raise error.CompilerException
      except error.CompilerException:
         pass
      except:
         self.fail("Couldn't raise a CompilerException with no parameters.")
      else:
         self.fail("Couldn't raise a CompilerException with no parameters.")


   def testWithParams(self):
      try:
         raise error.CompilerException, "One parameter"
      except error.CompilerException:
         self.fail("Shouldn't raise a CompilerException with 1 parameter.")
      except:
         pass
      else:
         self.fail("Couldn't raise a CompilerException with no parameters.")


if __name__ == '__main__':
   unittest.main()
