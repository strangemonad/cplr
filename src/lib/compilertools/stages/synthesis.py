""" XXX docs needed

"""

# XXX TEST untested.

def make(env):

   # XXX for now just hard code the cvm synthesis module. Come back and make 
   # this more like the analysis factory.
   from _platforms.cvm import synthesis_cvm
   return synthesis_cvm.make(env)
