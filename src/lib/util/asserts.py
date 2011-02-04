"""Provides extra assertion primitives.

Python's 'assert' primitive is too simplistic in some cases.

For example, while asserting that a particular code path isn't implemented is
very simple to do, is manually repetitive
(http://en.wikipedia.org/wiki/Don%27t_repeat_yourself) and doesn't narrate
semantics.

"""

from util import introspect


def NotImplemented():
   """Unconditionally assert because the code path isn't implemented.

   Parameters:
      None

   Results:
      None

   Side effects:
      Raises an AssertionError indicating the nature of the assertion.

   """

   assert False, "XXX: Not Implemented."


def Abstract():
   """XXX
   
   """

   caller = introspect.callerFrameRecord()
   raise NotImplementedError("'%s' at %s:%d is abstract." % \
                             (caller[3], caller[1], caller[2]))