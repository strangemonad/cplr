"""Extra introspection utilities.

Python provides a rich set of utilities to introspect the execution environment. However, there are still a few operations that might be useful.

"""

import inspect


def callerFrameRecord():
   """Get the caller's frame record.
   
   For example if a() calls b() and b() calls callerName() then the frame record 
   for a() will be returned.

   Parameters:
      None

   Results:
      The frame record of the caller that called this function. None if a caller 
      does not exist.

   Side effects:
      None

   """

   caller = None
   try:
      caller = inspect.getouterframes(inspect.currentframe())[2]
   except IndexError:
       pass

   return caller
