
import commands
import os
import shutil
import tempfile

from compilertools import environment

_CPLR_NAMESPACE = "cplr"
_CPLR_INCLUDE = os.path.join(_CPLR_NAMESPACE, "include")
_CPLR_LIB = os.path.join(_CPLR_NAMESPACE, "lib")

# XXX I don't know how to get directory of the current module
# XXX this assumes that cplr is being run from the top level.
_CVM_DIR = os.path.join("src", "lib", "compilertools", "stages", "_platforms", 
                       "cvm")


def link(env, obj, destination):
   # XXX TODO, the environment somehow would need to specify to link against the
   # ADA runtime or CVM might provide a super rich runtime as well. We can hard
   # code for now
      
   assert obj
   assert env[environment.ENTRY_POINT]

   toolchainRoot = env[environment.TOOLCHAIN_ROOT]
   _validateCVM(toolchainRoot)
   _validateGC(toolchainRoot)


   combinedPath = _generateBound(obj, env[environment.ENTRY_POINT])
   resultPath = ""
   try:
      resultPath = _gcc(toolchainRoot, combinedPath)
      assert os.path.isfile(resultPath)
      shutil.move(resultPath, destination)
   finally:
      os.remove(combinedPath)
      os.path.exists(resultPath) and os.remove(resultPath)


def _generateBound(obj, entryPoint):
   combinedPath = tempfile.mktemp(".c")
   combined = open(combinedPath, "w+")

   # XXX TODO. figure out how to make this posix compliant wrt the entry point.
   
   # Don't touch the spacing or indent of the string!
   completeProgram = r"""
   #include "cvm.h"
   
   #include "gc.h"

   %s

   int
   main()
   {
      GC_INIT();

      %s();

      return 0;
   }
""" % (obj, entryPoint)

   combined.write(completeProgram)
   combined.close()
   return combinedPath


def _validateCVM(toolchainRoot):
   includePath = _includePath(toolchainRoot)

   if not os.path.isfile(os.path.join(includePath, "cvm.h")):
      # Create the C VM on the fly.
      # This is really simple for now.
      os.path.isdir(includePath) or os.makedirs(includePath)
      shutil.copy(os.path.join(_CVM_DIR, "cvm.h"),
                  os.path.join(includePath, "cvm.h"))


def _validateGC(toolchainRoot):
   includePath = _includePath(toolchainRoot)

   if not os.path.isfile(os.path.join(includePath, "gc.h")):
      print "Building the Boehm Garbage Collector for the first time..."

      # XXX grab the prefix before changing working directories.
      prefix = _cplrNameSpacePath(toolchainRoot)
      oldWD = os.getcwd()
      os.chdir(_gcSrcPath(toolchainRoot))

      try:
         
         cmd = "./configure --prefix=%s --disable-threads" % prefix
         (status, output) = commands.getstatusoutput(cmd)
         assert status == 0, "\n".join([cmd, output])

         cmd = "make"
         (status, output) = commands.getstatusoutput(cmd)
         assert status == 0, "\n".join([cmd, output])

         cmd = "make check"
         (status, output) = commands.getstatusoutput(cmd)
         assert status == 0, "\n".join([cmd, output])

         cmd = "make install"
         (status, output) = commands.getstatusoutput(cmd)
         assert status == 0, "\n".join([cmd, output])
         
      finally:
         cmd = "make clean"
         commands.getstatusoutput(cmd)

         os.chdir(oldWD)


def _gcc(toolchainRoot, source):
   """ Compile source to destination.
   
   This should always succeed.
   
   Returns the path where the results were written to.
   
   """
   
   destination = tempfile.mktemp()

   # XXX should we make gcc -pedantic and -ansi?
   # XXX TODO hould pass an optimization level in the environment.

   gccCommand = "gcc -Wall -Werror -I%s %s %s -o %s" % \
                (_includePath(toolchainRoot),
                 source, _libgc_aPath(toolchainRoot), destination)
   (status, output) = commands.getstatusoutput(gccCommand)
   assert status == 0, "\n".join([gccCommand, output])
   assert not output, "\n".join([gccCommand, output])

   return destination


def _cplrNameSpacePath(toolchainRoot):
   # XXX only works if CWD is correct wrt toolchainRoot (if toolchainRoot is a
   # relative path).
   return os.path.abspath(os.path.join(toolchainRoot, _CPLR_NAMESPACE))


def _includePath(toolchainRoot):
   return os.path.join(toolchainRoot, _CPLR_INCLUDE)


def _libPath(toolchainRoot):
   return os.path.join(toolchainRoot, _CPLR_LIB)


def _gcSrcPath(toolchainRoot):
   return os.path.join(toolchainRoot, "src", "gc6.7")


def _libgc_aPath(toolchainRoot):
   return os.path.join(_libPath(toolchainRoot), "libgc.a")