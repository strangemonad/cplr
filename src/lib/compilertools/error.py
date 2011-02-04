"""XXX docs

"""

# XXX docs - add literate comments.

class CompilerException(StandardError):
   """Base class for compiler exceptions.
   
   Other modules in compilertools may subclass and raise more specific variants.
   A CompilerException is raised when an exceptional situation arrises during 
   compilation and further progress can not be made. The exceptional situation 
   is not necessarily the result of the source content being compiled.
   
   """

   def __init__(self):
      StandardError.__init__(self)


# XXX TEST the remainder of the module is untested...

class CompilationIssue(object):
   """Base class for all issues found in the sources while compiling.

   CompilationIssues provide a way of identifying particular issues with the 
   source. Issues may or may not be fatal to the compilation.

   """

   def __init__(self, startIndex, endIndex):
      self.__source = "XXX TODO pretty print the source"
      self.__sname = ""
      self.__context = ""
      self.__start = startIndex
      self.__end = endIndex

   def setSourceName(self, sname):
      self.__sname = sname

   def setSourceContext(self, context):
      self.__context = context

   def endIndex(self):
      return self.__end


   def startIndex(self):
      return self.__start


   def __str__(self):
      # XXX TODO this will raise if ever source is not a file with a name.
      # Need to add a utility method to the io package to handle failure 
      # gracefullly.
      # XXX TEST with stdin, file, StringIO.
      # XXX TODO this makes it impossible to tell where the error originated 
      # from since the indices are character ranges. Change it so that it gets 
      # line info from the source.
      return "%s [%d : %d]\n%s" % \
             (self.__sname, self.__start, self.__end, self.__context)


class CompilationError(CompilationIssue):
   """Represents an error found in a source while compiling.
   
   A CompilationError arises directly as the result of a malformed or incorrect 
   source as defined by the source's language specification.
   
   """

   def __str__(self):
      return "ERROR: %s" % CompilationIssue.__str__(self)


class CompilationWarning(CompilationIssue):
   """Represents an unwise construct encountered in a source while compiling.
   
   A CompilationWarning arrises in situations when the language specification 
   leaves certain bahaviour to be implementation dependent.
   
   """

   def __str__(self):
      return "WARNING: %s" % CompilationIssue.__str__(self)
