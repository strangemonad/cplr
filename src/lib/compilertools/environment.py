""" XXX docs

"""

import os


# Keys
DIALECT="dialect"
ENTRY_POINT="entry-point"
LAST_PHASE="last-phase"
PLATFORM="platform"
TOOLCHAIN_ROOT="toolchain_root"


def default():
   env = empty()
   env[TOOLCHAIN_ROOT] = os.path.join(os.getcwd(), "toolchain")
   env[PLATFORM] = "cvm" # XXX hard code CVM for now.
   return env

def empty():
   return {}
