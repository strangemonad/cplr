import unittest

import pipeline


class PipelineTestCase(unittest.TestCase):

   def testEmpty(self):
      p = pipeline.Pipeline()
      source = "some input"
      (result, issues) = p(source)
      self.assertEqual(source, result)
      self.assertEqual([], issues)

   def testOnePhase(self):
      phases = [lambda source: (source.capitalize(), [1])]
      p = pipeline.Pipeline(phases)
      
      source = "some input"
      (result, issues) = p(source)
      self.assertEqual(source.capitalize(), result)
      self.assertEqual([1], issues)

   def testAveragePipeline(self):
      phases = [lambda source: (source + "1", []),\
                lambda source: (source + "2", []),\
                lambda source: (source + "3", []),]
      p = pipeline.Pipeline(phases)

      (result, issues) = p("")
      self.assertEqual("123", result)
      self.assertEqual([], issues)

   def testNonDestructive(self):
      phases = [lambda source: (source, [])]
      p = pipeline.Pipeline(phases)
      
      source = "some other input"
      (result, issues) = p(source)
      self.assertEqual(source, result)
      self.assertEqual([], issues)

   def testIssueAccumulation(self):
      phases = [lambda source: ("", [1]),\
                lambda source: ("", []),\
                lambda source: ("", [3]),\
                lambda source: ("", [3, 4, 5]),]
      p = pipeline.Pipeline(phases)

      (result, issues) = p("")
      self.assertEqual("", result)
      self.assertEqual([1, 3, 3, 4, 5], issues)

   def testRepeatedPhase(self):
      t = lambda source: (source[:-1], [])
      phases = [t, t, t, t, t]
      p = pipeline.Pipeline(phases)

      (result, issues) = p("Hello World!")
      self.assertEqual("Hello W", result)
      self.assertEqual([], issues)

   def testPhaseReplacement(self):
      phases = [lambda source: (source + "a", [1]),\
                lambda source: (source + "b", [2]),]
      p = pipeline.Pipeline(phases)

      p[1] = lambda source: (source + "c", [3])

      (result, issues) = p("")
      self.assertEqual("ac", result)
      self.assertEqual([1, 3], issues)
      
   def testPhaseInsertion(self):
      phases = [lambda source: (source + "a", [1]),\
                lambda source: (source + "b", [2]),]
      p = pipeline.Pipeline(phases)

      p[1:1] = [lambda source: (source + "c", [3])]

      (result, issues) = p("")
      self.assertEqual("acb", result)
      self.assertEqual([1, 3, 2], issues)
      
      p.insert(1, lambda source: ("", []))

      (result, issues) = p("")
      self.assertEqual("cb", result)
      self.assertEqual([1, 3, 2], issues)

   def testPhaseRemoval(self):
      phases = [lambda source: (source + "a", [1]),\
                lambda source: (source[:-4], []),\
                lambda source: (source*2, ["foo"]),\
                lambda source: (source+ "!", []),]
      p = pipeline.Pipeline(phases)

      del p[2]

      (result, issues) = p("Hey there")
      self.assertEqual("Hey th!", result)
      self.assertEqual([1], issues)
      
      p = pipeline.Pipeline(phases)
      p = p[2:]

   def testListRepetition(self):
      phases = [lambda source: (source + "1", []),\
                lambda source: (source, ["y"]),\
                lambda source: (source + "3", ["z"]),]
      p = pipeline.Pipeline(phases)

      p = p * 3
      
      (result, issues) = p("")
      self.assertEqual("131313", result)
      self.assertEqual(["y", "z", "y", "z", "y", "z"], issues)

   def testListConcatenation(self):
      phases = [lambda source: (source + "1", []),\
                lambda source: (source, ["y"]),\
                lambda source: (source + "3", ["z"]),]
      p = pipeline.Pipeline(phases)

      phases = [lambda source: (source + "a", [1]),\
                lambda source: (source[:-3], []),\
                lambda source: (source*2, ["foo"]),\
                lambda source: (source+ "!", []),]
      p = p + pipeline.Pipeline(phases)
      
      (result, issues) = p("")
      self.assertEqual("!", result)
      self.assertEqual(["y", "z", 1, "foo"], issues)


   def testNullSourceShortCircuits(self):
      phases = [lambda source: (source + "1", ["x"]),\
                lambda source: (source + "2", ["y"]),\
                lambda source: (source + "3", ["z"]),]
      p = pipeline.Pipeline(phases)

      (result, issues) = p(None)
      self.assertEqual(None, result)
      self.assertEqual([], issues)
      
   def testNullResultShortCircuits(self):
      phases = [lambda source: (source + "1", ["x"]),\
                lambda source: (None, ["y"]),\
                lambda source: (source + "3", ["z"]),]
      p = pipeline.Pipeline(phases)

      (result, issues) = p("foo")
      self.assertEqual(None, result)
      self.assertEqual(["x", "y"], issues)

   def testReUse(self):
      phases = [lambda source: (source + "1", ["x"]),\
                lambda source: (source + "2", ["y"]),\
                lambda source: (source + "3", ["z"]),]
      p = pipeline.Pipeline(phases)

      (result, issues) = p("")
      self.assertEqual("123", result)
      self.assertEqual(["x", "y", "z"], issues)

      (result, issues) = p("")
      self.assertEqual("123", result)
      self.assertEqual(["x", "y", "z"], issues)
      
      (result, issues) = p("testing")
      self.assertEqual("testing123", result)
      self.assertEqual(["x", "y", "z"], issues)

   def testInvalidPhase(self):
      phases = [1, 2]
      p = pipeline.Pipeline(phases)
      
      source = "some input"
      self.assertRaises(TypeError, p.__call__, source)      
      
      phases = [None, None]
      p = pipeline.Pipeline(phases)
      
      source = "some input"
      self.assertRaises(TypeError, p.__call__, source)

   def testInvalidPhaseResult(self):
      phases = [lambda source: (source, None)]
      p = pipeline.Pipeline(phases)
      
      source = "some input"
      self.assertRaises(TypeError, p.__call__, source)      
      
      phases = [lambda source: source]
      p = pipeline.Pipeline(phases)
      
      source = "some input"
      self.assertRaises(ValueError, p.__call__, source)      


if __name__ == '__main__':
   unittest.main()
