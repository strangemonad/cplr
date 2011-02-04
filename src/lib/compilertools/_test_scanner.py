
import unittest

from scanner import ByteScanner
from StringIO import StringIO

class ByteScannerCreationTestCase(unittest.TestCase):

   def testNullSource(self):
      s = ByteScanner()
      self.assertRaises(AttributeError, s, None)

   def testNonFileSource(self):
      s = ByteScanner()
      self.assertRaises(AttributeError, s, "simple string")

   def testStringIOSource(self):
      try:
         s = ByteScanner()
         s(StringIO(""))
      except:
         self.fail("Couldn't run a ByteScanner on a StringIO instance")


class ByteScannerCallTestCase(unittest.TestCase):

   def testEmpty(self):
      s = ByteScanner()
      chars, issues = s(StringIO(""))
      self.assertEqual(chars, [('EOF', 0)])

   def testLength1(self):
      s = ByteScanner()
      chars, issues = s(StringIO("H"))
      self.assertEqual([("H", 0), ('EOF', 1)], chars)

   def testAverage(self):
      s = ByteScanner()
      chars, issues = s(StringIO("Hello\tWorld!\n"))
      expected = [('H', 0),
                  ('e', 1),
                  ('l', 2),
                  ('l', 3),
                  ('o', 4),
                  ('\t',5),
                  ('W', 6),
                  ('o', 7),
                  ('r', 8),
                  ('l', 9),
                  ('d', 10),
                  ('!', 11),
                  ('\n',12),
                  ('EOF',13)]
      self.assertEqual(chars, expected)


class ByteScannerResultToStringTestCase(unittest.TestCase):

   
   def testAverage(self):
      s = ByteScanner()
      chars, issues = s(StringIO("Hello\tWorld!\n"))
      expected = """('H', 0)
('e', 1)
('l', 2)
('l', 3)
('o', 4)
('\\t', 5)
('W', 6)
('o', 7)
('r', 8)
('l', 9)
('d', 10)
('!', 11)
('\\n', 12)
('EOF', 13)"""
      self.assertEqual(str(chars), expected)

if __name__ == '__main__':
   unittest.main()


# XXX TODO: All the tests so far use StringIO. Should try some with sockets and 
#           files
