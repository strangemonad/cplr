import unittest

import asserts


class AssertionsTestCase(unittest.TestCase):

   def testNotImplemented(self):
      self.assertRaises(AssertionError, asserts.NotImplemented)

      try:
         asserts.NotImplemented()
      except AssertionError, e:
         notImplementedMsg = "XXX: Not Implemented."

         # XXX exceptions in older versions of Python don't have the 'message' 
         # attribute. Instead look up the first argument.
         self.assertEqual(e.args[0], notImplementedMsg)
         self.assertEqual(str(e), notImplementedMsg)


if __name__ == '__main__':
   unittest.main()
