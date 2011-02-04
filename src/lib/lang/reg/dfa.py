

class UndefinedTransitionError(StandardError):
   pass


def match(string):
   # XXX TEST untested
   # XXX Avoid a circular import.
   import epsilon_nfa
   return epsilon_nfa.string(string).toDFA()


def matchIgnoreCase(string):
   # XXX TEST untested
   # XXX Avoid a circular import.
   import epsilon_nfa
   return epsilon_nfa.stringIgnoreCase(string).toDFA()
   
   # Note, the naive approach kills the Python interpreter on even moderately
   # large input strings:
   # return reduce(epsilon_nfa.alt,
   #                  map(epsilon_nfa.string, permuteCaps(string))).toDFA()
   #
   # This would temporarily create an alternation on 2^len(string) e-NFAs and 
   # then "reduce" them to a DFA on S(n) states where 
   # n = len(string) and 
   # S(n) = n*(n+1)*(2*n+1)/6.
   #
   # Note that the DFA is optimal and a smaller one can not be constructed. 
   # There is simply that much "memory" needed. Keeping the combinatorial
   # explosion to the very last step, toDFA(), is easier on the interpreter as 
   # there are a much smaller number of eNFA states to handle in the conversion.


class DFA(object):


   def __init__(self, startState):
      self.__startState = startState
      self.__currentState = None
      self.reset()


   def accepts(self):
      return self.__currentState.accepts()


   def run(self, symbol):
      self._validateStateMachine()
      self.__currentState = self.__currentState.transition(symbol)
      self._validateStateMachine()


   def reset(self):
      self.__currentState = self.__startState


   def _validateStateMachine(self):
      if not self.__currentState:
         raise UndefinedTransitionError


class _State(object):


   def transition(self, symbol):
      self.__validateSymbol(symbol)
      
      if not symbol in self.__transitions:
         return None
      else:
         return self.__transitions[symbol]


   def setTransition(self, symbol, state):
      self.__validateSymbol(symbol)
      if not state:
         raise TypeError, "DFA transitions must return a valid state."

      self.__transitions[symbol] = state


   def accepts(self):
      return self.__accepts


   def setAccepts(self):
      self.__accepts = True


   def __validateSymbol(self, symbol):
      if symbol == None:
         raise TypeError, "DFA transitions must be defined by a valid symbol."


   def __init__(self):
      self.__transitions = {}
      self.__accepts = False