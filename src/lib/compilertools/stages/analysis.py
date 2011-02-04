""" XXX comments

"""

from compilertools import environment
from compilertools import error


class UnsupportedDialectException(error.CompilerException):
   """Raised when the requested dialect is unsupported.
   
   """

   def __init__(self, dialect):
      error.CompilerException.__init__(self)
      self.__dialect = dialect

   def __str__(self):
      return "'%s' is not a supported source language." % self.__dialect


def makeAnalyzer(env):
   """An analyzer factory.

   Parameters:
      env - The environment 

   Results:
      (translator, complete) - A translator object and whether the translator 
                               converts a given source to an intermediate 
                               representation that is suitable to be processed 
                               by a synthesizer.
      
   Side effects:
      Will raise an AttributeError if env is not a valid environment.
      Will raise an UnsupportedDialectException if the dialect isn't supported.

   """

   # XXX complete docs.

   # XXX for now just hard code using the Ada front-end.
   # XXX it's also bad practice to put imports here rather than at the top of 
   # the file. It's OK in this case though because Frontend needs to be defined
   # before the ada front-end can subclass it.

   # XXX catch the possible attribute error here and raise a TypeError instead.
   if env.get(environment.DIALECT) == "ada":
      # XXX make this import dynamic based on the infered dialect.
      from _languages.ada import analysis_ada
      return analysis_ada.makeAnalyzer(env)
   else:
      raise UnsupportedDialectException(env.get(environment.DIALECT))


# XXX TODO - to document.
#
# Takes a source and optional language spec and spits out a CPLR-IR.
# 
# complete vs incomplete front-end (where to stop compilation based on flags)?
# 
# 
# Results:
#    XXX the intermediate representation (explain what this means, what 
#    about compiler options that control where compilation stops and what is 
#    output? That's not supported in A1 but will be later).
