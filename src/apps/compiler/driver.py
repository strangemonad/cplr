
""" XXX lot's of comments.

Comments about life, the universe, and everything.

"""

import os
import sys

from util import asserts

from compilertools import environment

import arguments
from compiler import Compiler


def main(args, compiler=None):
   """The entry point for CPLR's command line interface.
   
   It may be useful to call main programatically if you are writing a simple 
   wrapper around CPLR's command line interface. It is discouraged to try to 
   parse the output written to standard out to try an infer the source of the 
   error. Instead create a Compiler object directly and handle the exceptions 
   that may be raised.

   Parameters:
      arguments - A list of strings that control the compilation.
   
   Results:
      One of the following integer values:
      0 - The compilation succeeded.
      2 - The arguments were invalid.
      3 - The sources and output files determined from the arguments couldn't 
          be opened.
      4 - The compilation failed due to an error in the source content.
   
   Side effects:
      If the function returns successfully output may be written as directed by 
      the arguments.

      If the function returns an error code information about the error may be 
      printed to stderr.

      The function may never return and instead may raise any number of 
      exceptions if abnormal execution is encountered. 
      All raised exceptions are bugs. Note that cases such as invalid arguments 
      or failure to open a source file are expected to occur and will be 
      reported by the result rather than raising an error.

   """

   result = 0
   # Unified try:except:finally is a 2.5 feature
   try:
      try:
         sourceFiles = []

         (env, sources, output) = arguments.parse(args)

         sourceFiles = [open(source, "r") for source in sources]   
      except IOError, e:
         result = 3
         print >> sys.stderr, "'%s': %s" % (e.filename, e.strerror)

      else:
         compiler = compiler or Compiler(env)
         
         # XXX add support for compiling multiple sources at a time.
         (compilation, issues) = compiler.compile(sourceFiles[0])
         # (compilation, issues) = compiler.compile(sourceFiles)

         result = postProcess(env, output, compilation)
         
         for issue in issues:
            print >> sys.stderr, "%s\n" % str(issue)

   finally:
      for sourceFile in sourceFiles:
          sourceFile.close()
      
   return result

# The return code of 1 is purposefully left unused XXX
# stdout is reserved for piping.
# xxx change to return (status, message)


def postProcess(env, outputPath, obj):
   """A hacked up linker routine.
   
   Nothing too complicated for the time being. Expects the object to be 
   specified as CVM code. If the object can't be linked it will be written to 
   the outputPath instead. If it can be linked successfully the fully compiled 
   executable will be written to the outputPath.

   """

   if not obj:
      print >> sys.stderr, \
         "WARNING: The compilation didn't yield any results. "\
         "Nothing will be written to '%s'" % outputPath
      return 0

   entryPoint = env[environment.ENTRY_POINT]
   if entryPoint:
      # Link
      assert not env.get(environment.LAST_PHASE)

      entryPoint = obj.namespace + entryPoint
      if entryPoint in obj.symbols:
         # XXX need to check that entry point is a proc.
         env[environment.ENTRY_POINT] = entryPoint
         
         from compilertools.stages import link
         link.link(env, obj.fragment, outputPath)
      else:
         print >> sys.stderr, \
            "ERROR: '%s' is not a valid main procedure" % \
                     env[environment.ENTRY_POINT]
         return 1
         
   else:
      # Just write the output.
      try:
         outputFile = open(outputPath, "w")
         try:
            outputFile.write(str(obj))
         finally:
            outputFile.close()
      except IOError, e:
         print >> sys.stderr, \
            "ERROR: Couldn't write result to %s: %s" % (e.filename, e.strerror)
         return 1

   return 0


if __name__ == "__main__":

   exitStatus = 0
   try:
      exitStatus = main(sys.argv[1:])

   # In newer verisons of Python Exception, SystemExit, and KeyboardInterrupt 
   # all derive from a common base class. In 2.2 and older Exception IS the base 
   # class so we must work around this.
   except KeyboardInterrupt:
      raise
   except SystemExit:
      raise

   except Exception:
      if "CPLR_DEBUG" in os.environ:
         raise
      else:
         print >> sys.stderr, \
                  "Encountered an unexpected error - %s"\
                  % str(sys.exc_info()[1])
         exitStatus = 1

   sys.exit(exitStatus)

# XXX TODO: explain why we are catching Exception rather than simply catch all.

# XXX TODO: get the exit status values from constants in the right python
# package.
