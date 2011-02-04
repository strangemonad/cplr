import unittest

import epsilon_nfa


class FactoryTestCase(unittest.TestCase):
   # XXX TODO These could be tested much more heavily.
   # add tests for edge cases in parameters.

   def testSymbol(self):
      dfa = epsilon_nfa.symbol("a").toDFA()
      self.assert_(not dfa.accepts())
      dfa.run("a")
      self.assert_(dfa.accepts())
      self.assertRaises(Exception, dfa.run, "a")

      dfa = epsilon_nfa.symbol("a").toDFA()
      self.assert_(not dfa.accepts())
      self.assertRaises(Exception, dfa.run, "b")
      
      dfa = epsilon_nfa.symbol("").toDFA()
      self.assert_(not dfa.accepts())
      dfa.run("")
      self.assert_(dfa.accepts())
      self.assertRaises(Exception, dfa.run, "a")
      
      dfa = epsilon_nfa.symbol(None).toDFA()
      self.assert_(dfa.accepts())
      self.assertRaises(Exception, dfa.run, "c")

   def testEpsilon(self):
      dfa = epsilon_nfa.epsilon().toDFA()
      self.assert_(dfa.accepts())
      self.assertRaises(Exception, dfa.run, "c")
      self.assertRaises(Exception, dfa.run, None)

   
   def testAlt(self):
      a = epsilon_nfa.symbol("a")
      b = epsilon_nfa.symbol("b")
      aOrB = epsilon_nfa.alt(a, b).toDFA()

      self.assert_(not aOrB.accepts())
      aOrB.run("a")
      self.assert_(aOrB.accepts())
      self.assertRaises(Exception, aOrB.run, "b")
      
      aOrB.reset()
      self.assert_(not aOrB.accepts())
      aOrB.run("b")
      self.assert_(aOrB.accepts())
      self.assertRaises(Exception, aOrB.run, "b")
      
      aOrB = epsilon_nfa.alt(b, a).toDFA()

      self.assert_(not aOrB.accepts())
      aOrB.run("a")
      self.assert_(aOrB.accepts())
      self.assertRaises(Exception, aOrB.run, "a")
      
      aOrB.reset()
      self.assert_(not aOrB.accepts())
      aOrB.run("b")
      self.assert_(aOrB.accepts())
      self.assertRaises(Exception, aOrB.run, "a")
      
   def testCloncat(self):
      a = epsilon_nfa.symbol("a")
      b = epsilon_nfa.symbol("b")
      aAndB = epsilon_nfa.concat(a, b).toDFA()
      
      self.assert_(not aAndB.accepts())
      aAndB.run("a")
      self.assert_(not aAndB.accepts())
      aAndB.run("b")
      self.assert_(aAndB.accepts())
      self.assertRaises(Exception, aAndB.run, "a")
      
      aAndB.reset()
      self.assert_(not aAndB.accepts())
      self.assertRaises(Exception, aAndB.run, "b")
      self.assertRaises(Exception, aAndB.run, "a")
      
      aAndB = epsilon_nfa.concat(b, a).toDFA()
      
      self.assert_(not aAndB.accepts())
      aAndB.run("b")
      self.assert_(not aAndB.accepts())
      aAndB.run("a")
      self.assert_(aAndB.accepts())
      self.assertRaises(Exception, aAndB.run, "a")
      
      aAndB.reset()
      self.assert_(not aAndB.accepts())
      self.assertRaises(Exception, aAndB.run, "a")
      self.assertRaises(Exception, aAndB.run, "b")

   def testKleene(self):
      a = epsilon_nfa.symbol("a")
      aStar = epsilon_nfa.kleene(a).toDFA()
      
      self.assert_(aStar.accepts())
      aStar.run("a")
      self.assert_(aStar.accepts())
      aStar.run("a")
      self.assert_(aStar.accepts())
      aStar.run("a")
      self.assert_(aStar.accepts())
      aStar.run("a")

      self.assertRaises(Exception, aStar.run, "b")

   def testString(self):
      abcd = epsilon_nfa.string("abcd").toDFA()
      
      self.assert_(not abcd.accepts())
      abcd.run("a")
      self.assert_(not abcd.accepts())
      abcd.run("b")
      self.assert_(not abcd.accepts())
      abcd.run("c")
      self.assert_(not abcd.accepts())
      abcd.run("d")
      self.assert_(abcd.accepts())
      
      self.assertRaises(Exception, abcd.run, "a")


class ClosureTestCase(unittest.TestCase):

   def setUp(self):
      self.s6 = epsilon_nfa._State()

      self.s5 = epsilon_nfa._State()
      self.s5.addEpsilonTransition(self.s6)

      self.s4 = epsilon_nfa._State()
      self.s4.addTransition("c", self.s5)

      self.s3 = epsilon_nfa._State()
      self.s3.addEpsilonTransition(self.s4)

      self.s2 = epsilon_nfa._State()
      self.s2.addEpsilonTransition(self.s3)
      self.s2.addEpsilonTransition(self.s4)

      self.s1 = epsilon_nfa._State()
      self.s1.addEpsilonTransition(self.s2)
      self.s1.addTransition("a", self.s3)

   def testClosureOfNullSet(self):
      states = epsilon_nfa.EpsilonNFA(None, None)._closure(None)
      self.assertEqual(None, states)

   def testClosureOfEmptySet(self):
      states = epsilon_nfa.EpsilonNFA(None, None)._closure(set())
      self.assertEqual(set(), states)

   def testClosureOneStateNoEpsilonStransitions(self):
      states = epsilon_nfa.EpsilonNFA(None, None)._closure(set([self.s6]))
      self.assertEqual(set([self.s6]), states)

      states = epsilon_nfa.EpsilonNFA(None, None)._closure(set([self.s4]))
      self.assertEqual(set([self.s4]), states)

   def testClosureOneStateOneEpsilonStransition(self):
      states = epsilon_nfa.EpsilonNFA(None, None)._closure(set([self.s5]))
      self.assertEqual(set([self.s6, self.s5]), states)

   def testClosureOneStateMulipleEpsilonStransitions(self):
      states = epsilon_nfa.EpsilonNFA(None, None)._closure(set([self.s2]))
      self.assertEqual(set([self.s2, self.s3, self.s4]), states)
      
      states = epsilon_nfa.EpsilonNFA(None, None)._closure(set([self.s1]))
      self.assertEqual(set([self.s1, self.s2, self.s3, self.s4]), states)

   def testClosureMultipleStates(self):
      states = \
         epsilon_nfa.EpsilonNFA(None, None)._closure(set([self.s2, self.s4]))
      self.assertEqual(set([self.s2, self.s3, self.s4]), states)

   def testClosureMultipleStates(self):
      states = \
         epsilon_nfa.EpsilonNFA(None, None)._closure(set([self.s2, self.s4]))
      self.assertEqual(set([self.s2, self.s3, self.s4]), states)

      states = \
         epsilon_nfa.EpsilonNFA(None, None)._closure(set([self.s2, self.s5]))
      self.assertEqual(set([self.s2, self.s3, self.s4, self.s5, self.s6]), \
                       states)

      states = \
         epsilon_nfa.EpsilonNFA(None, None)._closure(set([self.s1, self.s6]))
      self.assertEqual(set([self.s1, self.s2, self.s3, self.s4, self.s6]), \
                      states)
                      
      states = \
         epsilon_nfa.EpsilonNFA(None, None)._closure(set([self.s1, self.s5]))
      self.assertEqual(set([self.s1, self.s2, self.s3, 
                            self.s4, self.s5, self.s6]), states)

class StateTestCase(unittest.TestCase):

   def testCreate(self):
      s = epsilon_nfa._State()
      self.assert_(not s.transitions("a"))
      self.assert_(not s.transitions("3"))
      self.assert_(not s.transitions("\n"))

      self.assertEqual(s.transitions("a"), frozenset())

   def testAddSingleTransition(self):
      s = epsilon_nfa._State()
      s1 = epsilon_nfa._State()

      s.addTransition("a", s1)
      self.assertEqual(s.transitions("a"), frozenset([s1]))

   def testAddLoopTransition(self):
      s = epsilon_nfa._State()

      s.addTransition("a", s)
      self.assertEqual(s.transitions("a"), frozenset([s]))

   def testAddMultipleTransitions(self):
      s = epsilon_nfa._State()
      s1 = epsilon_nfa._State()
      s2 = epsilon_nfa._State()
      s3 = epsilon_nfa._State()
      s4 = epsilon_nfa._State()

      s.addTransition("f", s1)
      s.addTransition("f", s2)
      s.addTransition("f", s4)
      s.addTransition("0", s3)

      self.assertEqual(s.transitions("f"), frozenset([s1, s2, s4]))
      self.assertEqual(s.transitions("0"), frozenset([s3]))

   def testOverwriteExistingTransitions(self):
      s = epsilon_nfa._State()
      s1 = epsilon_nfa._State()

      s.addTransition("f", s1)
      self.assertEqual(s.transitions("f"), frozenset([s1]))

      s.addTransition("f", s1)
      self.assertEqual(s.transitions("f"), frozenset([s1]))

   def testEpsilonTransitions(self):
      s = epsilon_nfa._State()
      s1 = epsilon_nfa._State()
      s2 = epsilon_nfa._State()

      s.addTransition(None, s1)
      self.assertEqual(s.transitions(None), frozenset([s1]))
      self.assertEqual(s.epsilonTransitions(), frozenset([s1]))

      s.addEpsilonTransition(s2)
      self.assertEqual(s.transitions(None), frozenset([s1, s2]))
      self.assertEqual(s.epsilonTransitions(), frozenset([s1, s2]))

   def testSetNullTransitionState(self):
      s = epsilon_nfa._State()
      self.assertRaises(TypeError, s.addTransition, "X", None)


if __name__ == '__main__':
   unittest.main()
