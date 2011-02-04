""" CVM synthesis factory.

"""


from ada_to_cvm import AdaToCVM


def make(env):
   return AdaToCVM()

# XXX TEST: none of this module is tested.
