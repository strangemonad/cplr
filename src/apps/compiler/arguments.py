""" The compiler's argument parser.

"""

# XXX literate docs.

from optparse import OptionParser

from compilertools import environment


def parse(args):
   """Make sense of an array of strings.

   Results:
   (environment, sources, output) - The environment in which to build
      an appropriate compiler and carry out the compilation. The list of strings
      that refer to source file names. The name of the file that should contain 
      the result of the compilation.
   
    Side effects:
      Might raise SystemExit with an error code of 2 if the arguments are 
      invalid.

   """

   parser = OptionParser(prog="cplr",
                         usage="cprl [options] source destination")
   
   # XXX flesh out more stop points (link, semantic, code gen)
   parser.add_option("--stop-after", dest=environment.LAST_PHASE,
                     help="Stop compilation after the specified phase - \
                           one of 'scanner', 'lexer', or 'parser'")
   
   parser.add_option("--main", dest=environment.ENTRY_POINT,
                     help="The name of the main procedure.\
                           If this isn't specified the program won't be linked\
                           into a final executable.")
   
   (options, args) = parser.parse_args(args)

   # XXX this next little lower casing bit is a quick hack. The right solution
   # would be to have a proper lower casing dictionary.
   option = getattr(options, environment.ENTRY_POINT)
   if option: setattr(options, environment.ENTRY_POINT, option.lower())  
   option = getattr(options, environment.LAST_PHASE)
   if option: setattr(options, environment.LAST_PHASE, option.lower())
   

   if getattr(options, environment.ENTRY_POINT) and \
      getattr(options, environment.LAST_PHASE):
      parser.error("Can't link an incomplete compilation. "\
                   "Specify either '--stop-after' or '--main.'")      

   # XXX TODO this is just changed to != 2 rather than < 2 for now. Need to add
   # support for compiling multiple sources at a time.
   if len(args) != 2:
      # parser.error("Expected 2 or more arguments but got %d" % len(args))
      parser.error("Expected 2 arguments but got %d" % len(args))

   env = environment.default()
   env.update(vars(options))
   return (env, args[:-1], args[-1])
