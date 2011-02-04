
import sys
import StringIO
import unittest

import arguments

class ParseArgumentsTestCase(unittest.TestCase):
   
   def setUp(self):
      # OptParse is annoying to unittest since it writes to std out.
      self.oldStdErr = sys.stderr
      sys.stderr = StringIO.StringIO()
      self.oldStdOut = sys.stdout
      sys.stdout = StringIO.StringIO()

   def tearDown(self):
      sys.stderr = self.oldStdErr
      sys.stdout = self.oldStdOut

   
   # XXX TEST should test valid environment creation as well.
   def testNoArguments(self):
      self.assertRaises(SystemExit, arguments.parse, [])

   def testOneArguments(self):
      self.assertRaises(SystemExit, 
                        arguments.parse, ["foo"])

   def testTwoArguments(self):
      (env, sources, output) = arguments.parse(["1", "2"])
      self.assertEqual("2", output, 
                       "'output' should contain the last positional argument")
      self.assertEqual(["1"], sources, 
                      "'sources' should be a list of all source files")

   # def testThreeArguments(self):
   #    (env, sources, output) = arguments.parse(["1", "2", "3"])
   #    self.assertEqual("3", output, 
   #                     "'output' should contain the last positional argument")
   #    self.assertEqual(["1", "2"], sources, 
   #                    "'sources' should be a list of all source files")


if __name__ == '__main__':
   unittest.main()
