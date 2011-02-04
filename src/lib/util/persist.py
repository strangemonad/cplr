"""Simple persistence helpers

"""

import cPickle as pickle


def loadOrCreate(factory, picklePath):
   """Try to load an object from the pickle otherwise create and persist it.
   
   """

   result = None
   pickleFile = None
   try:
      try:
         pickleFile = open(picklePath, "r")
         result = pickle.load(pickleFile)
      except:
         result = factory()

         pickleFile = open(picklePath, "w")
         pickle.dump(result, pickleFile, True)
   finally:
      pickleFile and pickleFile.close()
   
   return result
   