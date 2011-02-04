"""Programatically generate the main CPLR document.

The cplrdoc module is a poor-man's document setting engine. The different chapters and sections of the document are merely procedurally enumerated.

Note: the working directory should be set to the root of the CPLR sources.

"""

import os

import pylit

from util import asserts


TMP_LIT= os.path.join("build", "tmp_lit.txt")

# List the parts that make up the document All paths are relative to #.

files = [os.path.join("doc", "CPLR.txt"),
         os.path.join("doc", "Introduction.txt"),
         os.path.join("doc", "ThroughTheLookingGlass.txt"),
         os.path.join("cplr"),
         os.path.join("README.txt"),
         os.path.join("doc", "Design.txt"),
         # os.path.join("doc", "Unsupported.txt"),
         os.path.join("doc", "Reflections.txt")]
         
         # os.path.join("src", "apps", "compiler", "driver.py"),
         #os.path.join("doc", "NeededSections.txt")]

def genRST(path):
   """Writes the reStructuredText for the main CPLR document.
   
   The contents are written to the file located at path.
   """
   
   cplrRST = open(path, "w")
   for path in files:
      appendFile(path, cplrRST)
   cplrRST.close()


def appendFile(sourcePath, outfile):
   
   # If everything where already in reStructuredText this would be trivial since
   # docutils and rst support the include directive. In our case a file might
   # still need to be converted from source to reStructured text using PyLit.
   if sourcePath.endswith(".txt"):
      append(sourcePath, outfile)
   else:
      appendLiterateBlock(sourcePath, outfile)

   # These rst files may not expect to be concatenated together but they are 
   # all self contained. To make sure directives don't accidentally merge 
   # together add 2 spurious newlines.
   outfile.write("\n\n")

def appendLiterateBlock(sourcePath, outfile):
   """Convert the source to reStructuredText and write it to the output file.
   
   Parameters:
      sourcePath - the path to a source file to be processed by PyLit. If the 
                   source isn't python this function can be updated to include 
                   an optional comment style parameter to configure PyLit. The 
                   default for PyLit is "# ".
      outfile - the result of the conversion will be written into outfile 
                wherever the current seek position happens to be.

   """

   outfile.write("#%s%s:\n%s\n\n" %\
                (os.path.sep,
                sourcePath,
                "-" * (len(sourcePath) + len(os.path.sep) + 2)))
   pylit.main([sourcePath, TMP_LIT])
   append(TMP_LIT, outfile)
   os.remove(TMP_LIT)


def append(sourcePath, outfile):
   outfile.writelines([line for line in open(sourcePath, "r")])




