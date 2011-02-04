"""
An attempt at a BC-SLR(1,1) parser from ``An LR Substring Parser for Noncorrecting 
Syntax Error Recover''.

"""


from compilertools.error import CompilationError
import copy

class SyntaxError(CompilationError):
   """An error in the syntax.
   
   """

   def __str__(self):
      # XXX come back and figure out printing of erors.
      return "SYNTAX %s" % CompilationError.__str__(self)

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
		return type(self) == type(i2) and self.rule == i2.rule and self.dot == i2.dot
	def __ne__(self, i2):
		return not self.__eq__(self,i2)
	def __cmp__(self, i2):
		if type(self) != type(i2):
			return cmp(type(self), type(i2))
		if self.rule != i2.rule:
			return cmp(self.rule, i2.rule)
		return cmp(self.dot, i2.dot)
	def __hash__(self):
		return hash(type(self))^hash(self.rule) ^ hash(self.dot)
	def __repr__(self):
		s = str(self.rule.lhs) + ' ::= '
		for i in range(len(self.rule.rhs)):
			if self.dot == i:
				s += '.'
			s += str(self.rule.rhs[i])
		if self.dot == len(self.rule.rhs):
			s += '.'
		return s
class SuffItem(Item):
	def __repr__(self):
		s = str(self.rule.lhs) + ' ::= ...'
		for i in range(len(self.rule.rhs)):
			if self.dot == i:
				s += '.'
			if i >= self.dot:
				s += str(self.rule.rhs[i])
		if self.dot == len(self.rule.rhs):
			s += '.'
		return s


def closure(I, G):
	Q = list(I)
	J = set(I)
	while len(Q) > 0:
		i = Q.pop(0)
		B = i.dotV()
		for r in G.rules:
			if r.lhs == B:
				j = Item(r,0)
				if j not in J:
					Q.append(j)
					J.add(j)
			elif isinstance(i, SuffItem) and B == None:
				A = i.rule.lhs
				for dot in range(len(r.rhs)):
					if A == r.rhs[dot]:
						j = SuffItem(r, dot+1)
						if j not in J:
							Q.append(j)
							J.add(j)
				
	return frozenset(J)

def goto(I, X, G):
	J = set()
	for i in I:
		if i.dotV() != X:
			continue
		j = copy.copy(i)
		j.dot += 1
		J.add(j)
	return closure(J, G)

def items(G):
	inititems = set()
	for r in G.rules:
		for dot in range(len(r.rhs)):
			if r.rhs[dot] in G.T:
				inititems.add(SuffItem(r, dot))
	inititems = closure(inititems, G)
	print inititems
	acceptitems = closure(set([SuffItem(G.rules[0],3)]), G)
	C = set([inititems])
	Q = list(C)
	while len(Q) > 0:
		I = Q.pop(0)
		for X in G.V:
			J = goto(I, X, G)
			if J == set() or J in C:
				continue
			Q.append(J)
			C.add(J)
	return (inititems, acceptitems, C)


def tables(G):
	(Iinit,Iaccept,C) = items(G)
	action = {}
	gotot = {}
	for I in C:
		for i in I:
			if i.dotV() in G.T:
				a = i.dotV()
				J = goto(I,a,G)
				if J not in C:
					continue
				act = ('shift', J)
				if (I,a) in action and action[I,a] != act:
					print 'conflict: ' + str(I) + ' '+ str (a) + '\n' + str(act) + '\n' + str(action[I,a]) + '\n'
					return
				action[I,a] = act
			elif not isinstance(i, SuffItem) and i.dotV() == None: # A -> alpha . ugly, but meh
				for b in G.follow[i.rule.lhs]:
					act = ('reduce', i.rule)
					if (I,b) in action and action[I,b] != act:
						print I
						print 'conflict: ' + str(I) + ' ' + str(b) + '\n' + str(act) + '\n' + str(action[I,b]) + '\n'
						return
					action[I,b] = act
		for A in G.NT:
			J = goto(I,A,G)
			if J not in C:
				continue
			gotot[I,A] = J
	return (Iinit, Iaccept, action, gotot)


class SBC(object):
	def __init__(self, G):
		self.G = G
		self.Grev = G.rev()
		(self.init, self.accept, self.action, self.goto) = tables(self.G)
		(self.rinit, self.raccept, self.raction, self.rgoto) = tables(self.Grev)
	def parse(self, w):
		xs=[]
		x = []
		e=[]
		S=[self.init]
		pos = 0
		while True:
			if pos >= len(w):
				break
			a = w[pos]
			ta = type(a)
			s = S[len(S)-1]
			if (s,ta) not in self.action: # error
				pos0 = self.pback(w, pos)
				e.append(SyntaxError(w[pos0].startIndex,w[pos].endIndex))
				xs.append(x)
				x = []
				S.append(self.init)
				if pos0 == pos: # not sure if this is right...could be non-terminating
					pos += 1
				#pos +=1
				continue
			(act, arg) = self.action[s,ta]
			if act == 'shift':
				S.append(arg)
				x.append(a)
				pos +=1
			elif act == 'reduce':
				x.append(arg)
				A = arg.lhs
				beta = arg.rhs
				del S[len(S)-len(beta):len(S)] # pop |beta| states
				s = S[len(S)-1]
				S.append(self.goto[s,A])
		xs.append(x)
		return (xs,e)
	def pback(self, w, pos):
		S=[self.rinit]
		while True:
			if pos < 0:
				break
			a = w[pos]
			ta = type(a)
			s = S[len(S)-1]
			if (s,ta) not in self.raction: # error
				return pos
			(act, arg) = self.raction[s,ta]
			if act == 'shift':
				S.append(arg)
				pos -= 1
			elif act == 'reduce':
				A = arg.lhs
				beta = arg.rhs
				del S[len(S)-len(beta):len(S)] # pop |beta| states
				s = S[len(S)-1]
				S.append(self.rgoto[s,A])
		return pos
