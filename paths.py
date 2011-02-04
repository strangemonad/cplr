"""Adjust the system search path.

Simply import this module to have sys.path adjusted to include the proper CPLR 
modules.

Note: this module must be included from an interpreter session with the working 
directory set to the root of the CPLR sources.

"""

import os
import sys


assert os.path.isdir("./src")

paths = [os.path.abspath("./src/lib"), \
         os.path.abspath("./src/apps/compiler"), \
         os.path.abspath("./toolchain/bin"), \
         os.path.abspath("./toolchain/lib"), \
         os.path.abspath("./tests"), \
         os.path.abspath("./doc"), \
        ]

for p in reversed(paths):
  sys.path.insert(1, p)
