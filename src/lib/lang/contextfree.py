

class Rule(object):


   def __init__(self, lhs, rhs):
      self.lhs = lhs
      self.rhs = rhs


   def __eq__(self, other):
      return self.lhs == other.lhs and self.rhs == other.rhs


   def __ne__(self, r2):
      return not self.__eq__(self,r2)

      
   def __cmp__(self, r2):
      # XXX does it make sense to implement compare? Rules really form a latice 
      # - not a total ordering.
      if self.lhs == r2.lhs:
         return cmp(self.rhs, r2.rhs)
      return cmp(self.lhs, r2.lhs)


   def __hash__(self):
      return hash(self.lhs) ^ hash(self.rhs)


   def __str__(self):
      s = str(self.lhs) + ' ::= '
      for A in self.rhs:
         s += str(A)
      return s
   
   def copy(self):
      return Rule(self.lhs, self.rhs)


class Grammar(object):


   def __init__(self, rules):
      self.rules = rules
   
      # XXX should these really be instance vars or can we just calculate them 
      # using getters?
      self.S = self.rules[0].lhs
      self.V = enumV(self.rules)
      self.NT = enumNT(self.rules)
      self.T = enumT(self.rules)
      self.nullable = enumNullable(self)
      self.first = enumFirst(self)
      self.follow = enumFollow(self)


   def rev(self):
      revrules = []
      for rule in self.rules:
         revrule = Rule(rule.lhs, tuple(reversed(rule.rhs)))
         revrules.append(revrule)
      return Grammar(revrules)


   def __str__(self):
      rstr = ''
      for r in self.rules:
         rstr += str(r) + '\n'
      return str(self.NT) + '\n' \
         + str(self.T) + '\n' \
         + rstr


def enumNT(rules):
   NT = set()
   for r in rules:
      NT.add(r.lhs)
   return NT
def enumT(rules):
   return enumV(rules) - enumNT(rules)
def enumV(rules):
   V = set()
   for r in rules:
      V.add(r.lhs)
      V |= set(r.rhs)
   return V

def enumNullable(G):
   N = {}
   for X in G.V:
      N[X] = False
   done = False
   while not done:
      done = True
      for r in G.rules:
         n = True
         for X in r.rhs:
            n &= N[X]
         done &= not n or N[r.lhs]
         N[r.lhs] |= n
   return N

def nullable(Xs, G):
   for X in Xs:
      if not G.nullable[X]:
         return False
   return True

def enumFirst(G):
   F = {}
   for X in G.T:
      F[X] = set([X])
   for X in G.NT:
      F[X] = set()
   done = False
   while not done:
      done = True
      for r in G.rules:
         f = set()
         for X in r.rhs:
            f |= F[X]
            if not G.nullable[X]:
               break
         done &= (f-F[r.lhs]) == set()
         F[r.lhs] |= f
   return F
def first(Xs, G):
   f = set()
   for X in Xs:
      f |= G.first[X]
      if not G.nullable[X]:
         break
   return f
def enumFollow(G):
   F = {}
   for X in G.V:
      F[X] = set()
   done = False
   while not done:
      done = True
      for r in G.rules:
         for i in range(0, len(r.rhs)):
            f = set()
            B = r.rhs[i]
            beta = r.rhs[i+1:]
            f |= first(beta, G)
            if nullable(beta, G):
               f |= F[r.lhs]
            done &= (f-F[B]) == set()
            F[B] |= f
   return F
def follow(Xs, G):
   f = set()
   for i in range(len(Xs)-1, -1, -1):
      f |= G.follow[Xs[i]]
      if not nullable(Xs[i:], G):
         break;
   return f



G = Grammar([
   Rule('Sp', (int, 'S', int)),
   Rule('S', ('A', float, 'B')),
   Rule('A', (str,)),
   Rule('A', (complex,)),
   Rule('B', (list,)),
   Rule('B', (tuple,)),
   Rule('B', ())
])
