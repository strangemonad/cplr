
# XXX TODO: refactor this. It's almost a complete duplicate of
# compilertools.stages.analysis and synthesis.

from compilertools import environment
from compilertools import error


class UnsupportedPlatformException(error.CompilerException):
   """Raised when the requested dialect is unsupported.
   
   """

   def __init__(self, dialect):
      error.CompilerException.__init__(self)
      self.__dialect = dialect

   def __str__(self):
      return "'%s' is not a supported source language." % self.__dialect


# XXX only support linking a single object file for now.
def link(env, obj, outputPath):
   """A multi platform linker
   
   XXX docs

   """

   # XXX complete docs.

   # XXX for now just hard code using C macro VM.

   if env.get(environment.PLATFORM) == "cvm":
      # XXX make this import dynamic based on the infered dialect.
      from _platforms.cvm import link_cvm
      return link_cvm.link(env, obj, outputPath)
   else:
      raise UnsupportedPlatformExceptionException(env.get(environment.PLATFORM))
