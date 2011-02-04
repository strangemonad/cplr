
import copy

import dfa


# Factory functions for constructing epsilon-NFAs.

# There are 5 primary epsilon-NFA constructions:
# symbol - the automaton that accepts only the given symbol.
# epsilon - the automaton that accepts the empty string.
# alternation - the automaton that accepts strings of either given automaton.
# concatenation - the automaton that accepts the concatenation.
# keene closure - 0 or more repetitions.

# XXX TODO language syntaxes would be much simpler to express if we provide
# overloaded | & * operators.

# XXX the factory methods that take DFAs are destructive. The deepcopy()
# function provided by the copy module seems to be pretty dumb when dealing
# with cycles. In order to make this non-destructive we would have to write a
# proper copy() routine for eNFAs.

# XXX the DFA conversion may be improved by a constant to linear amount of
# time by making the NFA's simpler as they are combined. In particular an NFA
# composed of kleene(alt(some set of NFAs)) currently produces a particularly
# bad degenerate NFA graph.

def symbol(sym):
   finalState = _State()
   startState = _State()
   startState.addTransition(sym, finalState)
   return EpsilonNFA(startState, finalState)


def epsilon():
   return symbol(None)


def alt(eNFA1, eNFA2):
   finalState = _State()
   startState = _State()
   
   startState.addEpsilonTransition(eNFA1._startState)
   startState.addEpsilonTransition(eNFA2._startState)

   eNFA1._finalState.addEpsilonTransition(finalState)
   eNFA2._finalState.addEpsilonTransition(finalState)
   
   return EpsilonNFA(startState, finalState)


def concat(eNFA1, eNFA2):   
   eNFA1._finalState.addEpsilonTransition(eNFA2._startState)

   return EpsilonNFA(eNFA1._startState, eNFA2._finalState)



def kleene(eNFA):
   eNFA._finalState.addEpsilonTransition(eNFA._startState)

   return EpsilonNFA(eNFA._startState, eNFA._startState)


# The remaining factory methods are merely utilities. They don't add any more 
# expressive power over the original 5.

def string(string):
   # XXX TEST: untested
   return reduce(concat, [symbol(char) for char in string])

def stringIgnoreCase(string):
   # XXX TEST: untested
   charMatches = [alt(symbol(char.lower()), symbol(char.upper())) \
                     for char in string]
   return reduce(concat, charMatches)


class EpsilonNFA(object):


   def __init__(self, startState, finalState):
      self._startState = startState
      self._finalState = finalState


   def toDFA(self):
      startStateSet = frozenset(self._closure([self._startState]))
      startDFAState = dfa._State()
      if self._finalState in startStateSet:
         startDFAState.setAccepts()

      equivalentDFA = dfa.DFA(startDFAState)
      
      knownStates = {startStateSet : startDFAState}

      incompleteStatesQueue = [(startStateSet, startDFAState)]
      while incompleteStatesQueue:
         (currentStateSet, currentDFAState) = incompleteStatesQueue.pop()

         virtualNFAState = _State()
         virtualNFAState.subsume(currentStateSet)
         for (symbol, nextStateSet) in virtualNFAState:
            nextStateSet = self._closure(nextStateSet)
            if symbol == None:
               # XXX TODO: make _closure() not include the epsilon transitions.
               continue

            nextDFAState = None
            if nextStateSet in knownStates:
               nextDFAState = knownStates[nextStateSet]
            else:
               nextDFAState = dfa._State()
               knownStates[nextStateSet] = nextDFAState
               incompleteStatesQueue.append((nextStateSet, nextDFAState))

            if self._finalState in nextStateSet:
               nextDFAState.setAccepts()

            currentDFAState.setTransition(symbol, nextDFAState)

      return equivalentDFA


   def _closure(self, states):
      partialClosure = None
      nextReachableStates = states

      while partialClosure != nextReachableStates:
         partialClosure = nextReachableStates
         nextReachableStates = set(partialClosure)
         for state in partialClosure:
            nextReachableStates |= state.epsilonTransitions()

      return partialClosure and frozenset(partialClosure)


   def __or__(self, eNFA):
      return alt(self, eNFA)


   def __and__(self, eNFA):
      return concat(self, eNFA)

   def __str__(self):
      return "%s\n" % self._startState


class _State(object):


   def addTransition(self, symbol, transition):
      if not transition:
         raise TypeError, "epsilon-NFA transitions must return a valid state."

      if not symbol in self.__symbolToTransitions:
         self.__symbolToTransitions[symbol] = set()
      self.__symbolToTransitions[symbol].add(transition)


   def addEpsilonTransition(self, transition):
      self.addTransition(None, transition)


   def transitions(self, symbol):
      return frozenset(self.__symbolToTransitions.get(symbol, []))


   def epsilonTransitions(self):      
      return self.transitions(None)


   def subsume(self, states):
      """Updates the behaviour of the current state to include the given states.
      
      Parameters:
         states - A collection of states that can be iterated over.
      
      Results:
         None
      
      Side effects:
         The instance will be updated to behave like the union of itself and the 
         given states.

      """

      # XXX TEST. This method is untested. 
      for state in states:
         for (symbol, transitions) in state.__symbolToTransitions.items():
            for transition in transitions:
               self.addTransition(symbol, transition)


   def __init__(self):
      self.__symbolToTransitions = {}


   def __iter__(self):
      return iter([(symbol, frozenset(transitions)) \
                    for (symbol, transitions) in \
                    self.__symbolToTransitions.items()])


   def __str__(self):
      return "%s\n" % self.__symbolToTransitions
