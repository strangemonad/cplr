""" Implementation of the pipeline architecture pattern.

"""

# XXX doc - how making a pipeline a list is good.


class Pipeline(list):
   """A pipeline of translator objects.
   
   The pipeline is itself by definition a translator object. An empty pipeline 
   is equivalent to the identity translator. If at any point the result of the 
   translation is 'None' further processing is stopped.
   
   """

# xxx literate docs:

   def __call__(self, source):
      result = source
      issues = []
 
      for translate in self:
         if result == None:
            break

         (result, moreIssues) = translate(result)
         issues.extend(moreIssues)

      return (result, issues)

# XXX literate docs:

   def __add__(self, other):
      return Pipeline(list.__add__(self, other))
   
   def __mul__(self, other):
      return Pipeline(list.__mul__(self, other))
   

# XXX todo might be nice to verify translators as they are added to catch errors 
# sooner - raise a TypeError on setting.
