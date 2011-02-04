""" The compiler object

XXX fill in

"""

from compilertools import environment
from compilertools.stages import analysis
from compilertools.stages import synthesis
from compilertools import pretty_print


# XXX do I really need a compiler object model or can I simply have a
# compile(compilationUnits, environment=None) function?

class Compiler(object):


   def __init__(self, environment=environment.default()):
      self.__environment = environment


   def compile(self, source):
      """Compile the sources.
      
      Compilation is controlled by the environment used to create the compiler.
      
      Parameters:
         sources - A list of file-like objects opened for reading.

      Results:
         (result, issues) - Result is a string containing the result of 
                            compiling all the sources. Issues is a list of 
                            issues (possibly empty) encountered while compiling. 
                            Result will be 'None' if any of the issues were 
                            fatal.
      
      Side effects:
         Once this function returns, the Compiler object itself has no side 
         effects and can be re-used in subsequent compilations.
         
         IOError
         UnsupportedDialectException
         XXX what exceptions can be raised?

      """

      result = None
      issues = []

      # XXX TODO accept multiple sources.
      
      process = self.__completePipline(source)
      (result, issues) = process(source)

      self._elaborateIssues(issues, source)

      return (result, issues)


   def __completePipline(self, source):
      # XXX TODO infer type from source.
      # XXX TEST dialect is inferred if none is set when creating the compiler.
      # XXX TEST manually setting the dialect overrides inference.
      frontEndEnv = self.__environment.copy()
      frontEndEnv[environment.DIALECT] = "ada"

      (pipeline, yeildsIR) = analysis.makeAnalyzer(frontEndEnv)
      if yeildsIR:
         pipeline.append(synthesis.make(self.__environment.copy()))

      return pipeline

   def _elaborateIssues(self, issues, source):
      for issue in issues:
         issue.setSourceName(source.name)
         p = pretty_print.pp_slice_f(source,
                                     issue.startIndex(), issue.endIndex())
         issue.setSourceContext(p)


# The slowest part of the compiler is the DFA constructions for the lexer and 
# parser. Thankfully the completed DFAs can be cached and reused. If it's 
# available use psyco to speed things up.

try:
   import psyco
   psyco.bind(Compiler.compile)
except ImportError:
   pass


# XXX some random comments that I've left as notes to myself.

# XXX the ada specific entry point specified at bind & time is part of the
# environment.
      
# needs to return the transformed result. What about multiple compilation 
# units? Should it return an array of object files or intermediate 
# results? Contatenated results? What about program binding and linking? 
# Returns a .o vs a .a?

# XXX how to control stopping at various phases of compilation.

# XXX validate compilationUnits?

# XXX right now we only accept ada so we only need 1 type of front end. In 
# the future each compilation unit might be a different language. Need a 
# map from languages types (possibly compilation units) to front end 
# instances. Note, the frontends could be buit on demand for each 
# compilation unit and cached.


# XXX for any given compilation the environment specifies the platform
# that the back-end should generate so we only need 1 backend.      


# XXX we are iterating here but we very well might want to fork and join.
# But our front ends can't be used concurrently right now since they 
# contain state about how far they have seeked into the source, 
# intermediate parse trees, etc. We would need multiple front ends and 
# backends if we wanted to multi-thread the compilation. With the way 
# compilers are currently invoked by build systems it makes much more 
# sense to build the concurrency at that level. We may want to 
# (re-)enforce this at our top level API and only accept 1 compilation 
# unit per invocation.
