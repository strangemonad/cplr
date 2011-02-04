"""System and integration test harness.

This whole thing could probably be done with the NOSE framework but it seemed overly complex and I couldn't wrap my head around it.

"""

import commands
import inspect
import re
import os
from os import path
import stat
from StringIO import StringIO
import sys

from util import asserts

from compilertools import environment

from compiler import Compiler
import driver


# XXX TODO the whole reporting of errors needs to be improved.


TMP_OUT = path.join("tests", "tmp")
# XXX need a DEV_NULL constant

RESULT_EXT = ".expect"
RUN_RESULT_EXT = ".expect_run"


def testCommandLine():

   # XXX TODO change this to use TMP_OUT or define a NULL_OUT or DEV_NULL

   cmd = "./cplr"
   (status, output) = commands.getstatusoutput(cmd)
   assertEqual(2, statusToExit(status))
   assert output.lower().startswith("usage: "), \
          "'%s' should print usage info" % cmd

   cmd = "./cplr --help"
   (status, output) = commands.getstatusoutput(cmd)
   assertEqual(0, statusToExit(status))
   assert output.lower().startswith("usage: "), \
          "'%s' should print usage info" % cmd

   cmd = "./cplr --main"
   (status, output) = commands.getstatusoutput(cmd)
   assertEqual(2, statusToExit(status))
   assert output.lower().startswith("usage: "), "'%s' should print usage info" % cmd
   assert output.find("cplr: error: --main"), \
          "'%s' should warn about invalid option usage" % cmd

   cmd = "./cplr --stop-after"
   (status, output) = commands.getstatusoutput(cmd)
   assertEqual(2, statusToExit(status))
   assert output.lower().startswith("usage: "), \
          "'%s' should print usage info" % cmd
   assert output.find("cplr: error: --main"), \
          "'%s' should warn about invalid option usage" % cmd

   cmd = "./cplr --stop-after foo --main bar"
   (status, output) = commands.getstatusoutput(cmd)
   assertEqual(2, statusToExit(status))
   assert output.lower().startswith("usage: "), \
          "'%s' should print usage info" % cmd


   cmd = "./cplr foo"
   (status, output) = commands.getstatusoutput(cmd)
   assertEqual(2, statusToExit(status))
   assert output.lower().startswith("usage: "), \
          "'%s' should print usage info" % cmd

   source = path.join("tests", "ada", "complete", "hello_ada_correct.ada")
   out = path.join("/", "dev", "null")
   cmd = "./cplr %s %s" % (source, out)
   (status, output) = commands.getstatusoutput(cmd)
   assertEqual(0, statusToExit(status))
   assertEqual("", output, "'%s' should not print any output." % cmd)
   
   # XXX need to test 3 params edge case.

def testCreateDriverWithCompilerInstance():
   source = path.join("tests", "scanner", "average_text_correct")
   
   env = environment.empty()
   env[environment.LAST_PHASE] = "scanner"
   result = driver.main([source, TMP_OUT], compiler=Compiler(env))
   assertEqual(0, result)
   assertNoDiff(TMP_OUT, source + ".expect")
   os.remove(TMP_OUT)


def testWritesCorrectOutput():
   # XXX TEST this inherently tests 2 things and obscures that this is the only 
   # place the scanner is system tests.
   assertCompilation(path.join("tests", "scanner", "average_text_correct"),
                     "--stop-after=scanner")

def testAdaLexer():
   sourceDir = path.join("tests", "ada", "lexer")
   sources = [path.join(sourceDir, "reserved_words_correct"),
              path.join(sourceDir, "comments_correct"),
              path.join(sourceDir, "string_lit_smoke_correct")]
   
   assertMultipleCompilations(sources, "--stop-after=lexer")


def testAdaFilter():
   source = path.join("tests", "ada", "filter", "average_correct")

   assertCompilation(source, "--stop-after=token-filter")


def testAdaFullCompilation():
   sourceDir = path.join("tests", "ada", "complete")
   sources = []
   assertCompilation(path.join(sourceDir, "hello_ada_correct.ada"),
                     options="--main hello")


def testAdaWarnings():
   sourceDir = path.join("tests", "ada", "complete")
   
   sources = [path.join(sourceDir, "compilation", "empty_body_warning.adb"),
              path.join(sourceDir, "compilation", "empty_spec_warning.ads")]
   
   assertMultipleCompilations(sources, expectedCmdOutputStartsWith="WARNING:")



# List the names of the functions to test. This could be auto-collected.
tests = [testCommandLine,
         testCreateDriverWithCompilerInstance,
         testWritesCorrectOutput,
         testAdaLexer,
         testAdaFilter,
         testAdaFullCompilation,
         testAdaWarnings]


################################################################################


def runTests(out=sys.stdout, verbosity=1):
   """Run the system and integration tests.
   
   XXX This could probably yanked out and made into a generic testing harness.

   Parameters:
      out - optionally a file like object where test output will be written. If 
            out isn't specified stdout will be used.

   Results:
      0 on success of all tests, 1 otherwise.

   Side effects:
      None

   """

   numTestsRun = 0
   numTestsFailed = 0

   for test in tests:
      if verbosity > 1:
         print test.__name__
      # Unified try:except:finally is a 2.5 feature
      try:
         try:
            test()
         except AssertionError, e:
            numTestsFailed += 1
            trace = inspect.trace()
            try:
               failedTestFrame = trace[-2]
               parentFrame = trace[-3]
            except IndexError:
               failedTestFrame = trace[-1]
               parentFrame = trace[-2]

            print "============================================================"
            print "TEST FAILED:"
            print "%s\n'%s' at %s:%d.\n'%s' at %s:%d.\n" % \
                  (test.__name__,
                  parentFrame[3], parentFrame[1], parentFrame[2],
                  failedTestFrame[3], failedTestFrame[1], failedTestFrame[2])
            print str(e)

      finally:
         numTestsRun += 1

   # Icky icky hacky! Some tests don't clean up after themselves.
   path.exists(TMP_OUT) and os.remove(TMP_OUT)

   print
   print "---------------------------------------------------------------------"
   print "Ran %d test%s" % (numTestsRun, numTestsRun != 1 and "s" or "")
   if numTestsFailed > 0:
      print "FAILED %d" % numTestsFailed
   else:
      print "OK"

   return numTestsFailed and 1


# XXX could move this to use the NOSE framework and use unittest assert 
# primitives.

def assertEqual(expected, result, message=""):
   assert expected == result, \
          "Expected %s but got %s \n\t%s" % \
          (str(expected), str(result), message)

def assertNoDiff(file1, file2):
   cmd = "diff %s %s" % (file1, file2)
   output = commands.getoutput(cmd)
   assert "" == output, "'%s' and '%s' differ - \n%s" % (file1, file2, output)

def assertCompilation(source, options="",
                      expectedExitStatus=0,
                      expectedCmdOutput="", expectedCmdOutputStartsWith=None):
   """Compiles the specified sources with the given options.
   
   Will assert that cplr returned the expected status and output.
   Will compare the result written by cplr with source.expect if it exists.
   Will run and campare the result printed by the compiled program with 
   source.expect_run if it exists.
   
   """

   cmd = "./cplr " + " ".join([options, source, TMP_OUT])

   (status, output) = commands.getstatusoutput(cmd)
   
   assertEqual(expectedExitStatus, statusToExit(status), cmd)

   if expectedCmdOutputStartsWith != None:
      assert output.startswith(expectedCmdOutputStartsWith), \
             "'%s' should output %s" % (cmd, repr(expectedCmdOutputStartsWith))
   else:
      assertEqual(output, expectedCmdOutput)

   expectedResult = source + ".expect"
   if os.path.isfile(expectedResult):
      assertNoDiff(TMP_OUT, expectedResult)
   
   expectedRunOutput = expectedResult + "_run"
   if os.path.isfile(expectedRunOutput):
      os.chmod(TMP_OUT, stat.S_IREAD|stat.S_IWRITE|stat.S_IEXEC)
      output = commands.getoutput(TMP_OUT)
      results = open(TMP_OUT, "w")
      results.write(output)
      results.close()
      assertNoDiff(TMP_OUT, expectedRunOutput)

   os.path.isfile(TMP_OUT) and os.remove(TMP_OUT)


def assertMultipleCompilations(sources, options="",
                               expectedExitStatus=0,
                               expectedCmdOutput="",
                               expectedCmdOutputStartsWith=None):

   # XXX could simply accept **kws here instead of duplicating the signature.
   for source in sources:
      assertCompilation(source, options, expectedExitStatus, expectedCmdOutput,
                        expectedCmdOutputStartsWith)


def statusToExit(status):
   """Convert a wait() style status number to an exit() value.
   
   Note, this ignores possible termination due to a signal.
   
   Parameters:
      status - The 16-bit status number.
   
   Results:
      The high 8 bits corresponding to the exit value.
   
   Side effects:
      None

   """
   
   return status >> 8

   
if __name__ == "__main__":
   sys.exit(runTests(tests))
