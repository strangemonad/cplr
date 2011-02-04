"""A list that pretty prints its string output rather than printing the repr of its contents.

"""

class PrettyPrintingList(list):

   def __str__(self):
      return "\n".join([str(item) for item in self])
