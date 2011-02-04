
from lang.contextfree import Grammar, Rule

from compilertools.error import CompilationError
from compilertools.lex import token


# The SLRParser implemented in this module expects to be created with an
# augmented grammar. In particular the parser expects a token stream with the
# begining and end of file markers at the very least. Language definitions
# shouldn't be concerned with this peculiarity. Language grammars can instead
# be passed to the following factory to build a valid
# lang.contextfree.Grammar. Needless to say the grammar rules themselves still
# must form a valid slr grammar.

def makeGrammar(rules):
   # In particular, the first rule of an SLR grammar must be:
   first = Rule("<SLR_AUGMENTED_START>", (token.BOF, rules[0].lhs, token.EOF))
   rules.insert(0, first)

   return Grammar(rules)


_SHIFT_ACTION = "shift"
_REDUCE_ACTION = "reduce"


class SyntaxError(CompilationError):
   """An error in the syntax.

   """

   def __str__(self):
      return "SYNTAX %s" % CompilationError.__str__(self)


class Parser(object):

   def __init__(self, grammar):
      # Note, self.action maps (state X TokenType) -> (parse action, Rule|state)
      (self.init, self.accept, self.action, self.goto) = tables(grammar)
      assert self.accept != None

   def __call__(self, tokens):
      return self.parse(tokens)


   def parse(self, tokens):
      # XXX TODO. There's a design conflict here. On the one side it would be
      # nice to have an isolate object that can simply parse without being
      # conserned of a keeping track of returning a derivation or parse tree. On
      # the other the Parser object itself should be the one to return a parse
      # tree for later Translators to act on. So this parse method will
      # currently do both. In the future it would be nice to move the slr
      # parsing logic to a lower level module (most likely lang.cfg) and have
      # top level parsers like this one just drive that logic.
      # Note, this is the design split between the parser and parser generator.
      # It would still be nice to be able to NOT generate a parse tree.

      # This is not the typical SLR parser stack. It is augmented so that each
      # element is a tuple (state X Token|Node). This allows a parse
      # tree to be built as the parser is validating the syntax without loosing
      # information gathered during the lexical analysis.

      # The start state is a special case since parsing can never reduce past
      # this state. There is no Token type that symantically makes sense for the
      # augmented start state of an SLR grammar.
      stack = [(self.init, None)]
      pos = 0


      # XXX TODO This whole loop could be made more compact by nest 2 loops
      # 1) A for-loop over the tokens
      # 2) an inner while action == _REDUCE_ACTION else consume token.
      while pos < len(tokens):
         curToken = tokens[pos]

         (action, arg) = self.action.get((_peek(stack)[0], type(curToken)),
                                         (None, None))
         
         if action == _SHIFT_ACTION:
            state = arg
            _push(stack, (state, curToken))
            pos += 1

         elif action == _REDUCE_ACTION:
            rule = arg
            node = rule.lhs(**_popChildren(stack, len(rule.rhs)))
            _push(stack, (self.goto[_peek(stack)[0], rule.lhs], node))

         else:
            _push(stack, (None, None))
            break

      if _peek(stack)[0] == self.accept:
         # At this point we have consumed EOF. The top of the stack has the 
         # tuple ([<SLR_AUGMENTED_START> ::= BOF Compilation EOF .], EOF). All 
         # we really care about is the parse tree. We need to simulate a 
         # reduction to get at the compilation node.
         rhs = _popChildren(stack, 3)
         return (rhs["compilation_"], [])

      else:
         # XXX TODO much better error reporting.
         return None, [SyntaxError(curToken.startIndex(), curToken.endIndex())]


class Item(object):
   def __init__(self, rule, dot):
      self.rule = rule
      self.dot = dot
   def dotV(self):
      if self.dot == len(self.rule.rhs):
         return None
      else:
         return self.rule.rhs[self.dot]
   def __eq__(self, i2):
      return self.rule == i2.rule and self.dot == i2.dot
   def __ne__(self, i2):
      return not self.__eq__(self,i2)

   # XXX this method shouldn't be here.
   def __cmp__(self, i2):
      if self.rule == i2.rule:
         return cmp(self.dot, i2.dot)
      return cmp(self.rule, i2.rule)

   def __hash__(self):
      return hash(self.rule) ^ hash(self.dot)

   def __str__(self):
      prefix = " ".join([sym.__name__ for sym in self.rule.rhs[:self.dot]])
      suffix = " ".join([sym.__name__ for sym in self.rule.rhs[self.dot:]])
      lhs = getattr(self.rule.lhs, "__name__", self.rule.lhs)
      return "%s ::= %s . %s" % (lhs, prefix, suffix)


# this isn't working yet...problem, have to number item sets....
def tables(grammar):
   (Iinit, Iaccept, C) = items(grammar)
   iaccpet = Item(grammar.rules[0], 2)
   startsym = grammar.rules[0].lhs
   action = {}
   gotot = {}
   for I in C:
      for i in I:
         if i.dotV() in grammar.T:
            a = i.dotV()
            J = goto(I,a,grammar)
            if J not in C:
               continue
            act = (_SHIFT_ACTION, J)

            if (I,a) in action and action[I,a] != act:
               # XXX change this to a raised exceptions.
               print 'conflict: ' + str(i) + str (a) + '\n' + \
                     str(act) + '\n' + str(action[I,a]) + '\n'
               return # XXX this should raise

            action[I,a] = act
         elif i.dotV() == None: # A -> alpha . ugly, but meh
            for b in grammar.follow[i.rule.lhs]:
               act = (_REDUCE_ACTION, i.rule)

               # XXX change this to a raised exceptions.
               if (I,b) in action and action[I,b] != act:
                  print 'conflict: ' + str(b) + '\n' + \
                        str(act) + '\n' + str(action[I,b]) + '\n'
                  return # XXX this should raise

               action[I,b] = act
#     if iaccpet in I: # accept
#        print 'got accept'
#        eof = iaccpet.dotV()
#        act = ('accept', None)
#        if (I,eof) in action:
#           print 'conflict: \n' + str(act) + '\n' + str(action[I,eof]) + '\n'
#           return
#        action[I,eof] = act
      for A in grammar.NT:
         J = goto(I,A,grammar)
         if J not in C:
            continue
         gotot[I,A] = J
   return (Iinit, Iaccept, action, gotot)


# Make the parse method more readable by actually using ADT functions on a
# "stack" object. The stack is nothing more than a list. The pop function is
# augmented to return a list of items

def _push(stack, value):
   stack.append(value)

def _popChildren(stack, numItems):
   """Pop a dictionary of children off the stack.

   This takes an augmented (state X Token|Node) stack and pops numItems.
   
   The result is a dictionary of (name X Token|Node) elements. The result is 
   meant to be used directly as a keyword argument expansion to a Node 
   constructor.
   
   Consider a fictitious example, assume the stack looks like
   (stateZ, IntegerLiteral)
   (stateY, Plus)
   (stateX, IntegerLiteral)
   
   There might also be
   class Statement(Node):
      ...
      def __init__(integerLiteral_, plus_, integerLiteral_2):
      ...
   
   The results of this method is a dictionary such that
   Statement(**_popChildren(stack, 3)) works.
   
   In particular the type name is used as the parameter name.
   The first letter is always lower case.
   Multiple occurrences of a type of instance in the numItems topmost stack 
   elements will result in serialization starting with 2. 
   
   Popping 0 items returns the empty dictionary, as would be expected.

   """

   children = {}

   if not numItems:
      return children
   
   assert numItems <= len(stack), \
          "Can't pop %d items. The stack only has %d." % (numItems, len(stack))

   topmost = stack[-numItems:]
   del stack[-numItems:]

   for stackItem in topmost:
      symbol = stackItem[1]

      typeCount = 1
      paramName = type(symbol).__name__
      paramName = paramName[:1].lower() + paramName[1:] + "_"
      while paramName in children:
         typeCount += 1
         if typeCount == 2:
            paramName += str(typeCount)
         else:
            paramName = paramName[:-1] + str(typeCount)
      
      children[paramName] = symbol
   
   return children


def _peek(stack):
   return stack[len(stack) - 1]


def items(grammar):
   # XXX comments about the implications this has on the augmented grammar
   # format.
   inititems = closure(set([Item(grammar.rules[0], 0)]), grammar)
   acceptitems = closure(set([Item(grammar.rules[0],3)]), grammar)
   C = set([inititems])
   Q = list(C)
   while len(Q) > 0:
      I = Q.pop(0)
      for X in grammar.V:
         J = goto(I, X, grammar)
         if J == set() or J in C:
            continue
         Q.append(J)
         C.add(J)
   return (inititems, acceptitems, C)


def goto(I, X, grammar):
   J = set()
   for i in I:
      if i.dotV() != X:
         continue
      j = Item(i.rule, i.dot+1)
      J.add(j)
   return closure(J, grammar)



def closure(I, grammar):
   Q = list(I)
   J = set(I)
   while len(Q) > 0:
      i = Q.pop(0)
      B = i.dotV()
      for r in grammar.rules:
         if r.lhs != B:
            continue
         j = Item(r,0)
         if j not in J:
            Q.append(j)
            J.add(j)
   return frozenset(J)


# Some debugging help that should be moved elsewhere.

def dumpStack(stack):
   for stackItem in reversed(stack):
      dumpStackItem(stackItem)
      print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

def dumpStackItem(stackItem):
   # A stack item is a (State X Token|Node) pair
   print "(", type(stackItem[1]).__name__, ")"
   dumpState(stackItem[0])

def dumpStates(states):
   for state in states:
      dumpState(state)
      print

def dumpState(state):
   # A state is just a set of items.
   print "----------------------------"
   if not state:
      print "| ", None
   else:
      for item in state:
         print "| ", item
   print "----------------------------"
