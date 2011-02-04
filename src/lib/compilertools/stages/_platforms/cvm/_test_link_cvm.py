
import commands
import os
import tempfile
import unittest

from compilertools import environment
import link_cvm


class LinkTestCase(unittest.TestCase):

   def setUp(self):
      toolchainRoot = os.path.join(os.getcwd(), "toolchain")
      self.env = {environment.TOOLCHAIN_ROOT:toolchainRoot,
                  environment.ENTRY_POINT : "foo"}

      self.tmpDest = tempfile.mktemp()

   def tearDown(self):
      os.path.exists(self.tmpDest) and os.remove(self.tmpDest)

   def assertSuccessOutput(self, expectedText):
      self.assert_(os.path.isfile(self.tmpDest))
      
      (status, output) = commands.getstatusoutput(self.tmpDest)
      self.assertEquals(status, 0)
      self.assertEquals(output, expectedText)

   def testUseCVMOpcode(self):
      link_cvm.link(self.env, r"void foo(){CVM_VERSION}", self.tmpDest)
      self.assertSuccessOutput("You've compiled a C-VM program (version 1.0).")

   def testGarbageCollectionFragment(self):      
      fragment = r"""
      #include <assert.h>
      #include <stdio.h>
      #include <string.h>

      void
      foo()
      {
         char str[] = "Hello Garbage-collected World!";
         char *heapBuf = (char *)GC_MALLOC(sizeof str);
         assert(heapBuf != 0);
         assert(*heapBuf == 0);

         strcpy(heapBuf, str);
         printf("%s", heapBuf);
      }
      """

      link_cvm.link(self.env, fragment, self.tmpDest)
      self.assertSuccessOutput("Hello Garbage-collected World!")


   def testEmbededCProgramFragment(self):      
      fragment = r"""
      #include <assert.h>
      #include <stdio.h>
      #include <string.h>

      void
      foo()
      {
         char str[] = "Hello World!";
         printf("%s", str);
      }
      """

      link_cvm.link(self.env, fragment, self.tmpDest)
      self.assertSuccessOutput("Hello World!")


if __name__ == '__main__':
   unittest.main()
