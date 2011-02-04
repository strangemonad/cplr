import unittest

import environment


class FactoryTestCase(unittest.TestCase):

   def testCreateEmpty(self):
      env = environment.empty()
      self.assertNotEqual(None, env)


if __name__ == '__main__':
   unittest.main()
