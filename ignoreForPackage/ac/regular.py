Sigma = set([chr(i) for i in range(0,256)])

statecounter = 0
def newstate():
	global statecounter
	statecounter += 1
	return statecounter -1

class Tranexp(object):
	pass
class Epsilon(Tranexp):
	def toENFT(self):
		s = newstate()
		f = newstate()
		Q = set([s,f])
		delta = {(s,''): set([f])}
		return ENFT(Q,s,f,delta)
class Sym(Tranexp):
	def __init__(self, sym):
		self.sym = sym
	def toENFT(self):
		s = newstate()
		f = newstate()
		Q = set([s,f])
		delta = {(s,self.sym): set([f])}
		return ENFT(Q, s, f, delta)
class Alt(Tranexp):
	def __init__(self, tranexps):
		self.tranexps = tranexps
	def __str__(self):
		s = '('
		alts = ''
		for e in self.tranexps:
			s += alts + str(e)
			alts = '|'
		s += ')'
		return s
	def toENFT(self):
		s = newstate()
		f = newstate()
		Q = set([s,f])
		delta = {}
		delta[s,''] = set()
		for tranexp in self.tranexps:
			m = tranexp.toENFT()
			Q |= m.Q
			delta.update(m.delta)
			delta[s,''] |= set([m.s])
			delta[m.f,''] = set([f])
		return ENFT(Q,s,f,delta)
class Cat(Tranexp):
	def __init__(self, tranexps):
		self.tranexps = tranexps
	def __str__(self):
		s = '('
		cats = ''
		for e in self.tranexps:
			s += cats + str(e)
			cat = '.'
		s += ')'
		return s
	def toENFT(self):
		s = newstate()
		f = newstate()
		Q = set([s,f])
		delta = {}
		tf = s
		for tranexp in self.tranexps:
			m = tranexp.toENFT()
			Q |= m.Q
			delta.update(m.delta)
			delta[tf,''] = set([m.s])
			tf = m.f
		delta[tf,''] = set([f])
		return ENFT(Q,s,f,delta)
class Kleene(Tranexp):
	def __init__(self, tranexp):
		self.tranexp = tranexp
	def toENFT(self):
		m = self.tranexp.toENFT()
		s = newstate()
		f = newstate()
		Q = m.Q | set([s,f])
		delta = m.delta.copy()
		delta[(s,'')] = set([m.s, f])
		delta[(m.f,'')] = set([s])
		return ENFT(Q, s, f, delta)
class Opt(Tranexp):
	def __init__(self, tranexp):
		self.tranexp = Alt([Epsilon(), tranexp])
	def toENFT(self):
		return self.tranexp.toENFT()

class FT(object):
	pass

class DFT(FT):
	def __init__(self, Q, s, F, delta):
		self.Q = Q
		self.s = s
		self.F = F
		self.delta = delta
	def deltastar(self, p, x):
		for c in x:
			p = self.delta.get((p,c), 'error')
		return p
	def run(self, x):
		p = self.deltastar(self.s, x)
		return p in self.F
	def minimize(self):
		U = {}
		for p in self.Q:
			for q in self.Q-set([p]):
				r = frozenset([p,q])
				U[r] = 0
		for r in U:
			if len(r&self.F) == 1:
				U[r] = 1
		done = False
		while not done:
			done = True
			T = U.copy()
			for r in T:
				if T[r] == 1:
					continue
				s = set(r)
				p = s.pop()
				q = s.pop()
				for a in Sigma:
					p1 = self.delta.get((p, a), 'error')
					q1 = self.delta.get((q,a), 'error')
					if p1 == 'error' or q1 == 'error' or p1 == q1:
						continue
					s = frozenset([p1,q1])
					if T[s] == 1:
						U[r] = 1
						done = False
		ecs = []
		Q1 = self.Q.copy()
		while len(Q1) > 0:
			p = Q1.pop()
			ec = set([p])
			for q in Q1.copy():
				r = frozenset([p,q])
				if U[r]== 0:
					ec.add(q)
					Q1.remove(q)
			ec = frozenset(ec)
			ecs.append(ec)
		
		return ecs


class NFT(FT):
	def __init__(self, Q, s, F, delta):
		self.Q = Q
		self.s = s
		self.F = F
		self.delta = delta
	def deltastar(self, s, x):
		T = set([s])
		for c in x:
			R = set()
			for p in T:
				R |= self.delta.get((p,c), set())
			T = R
		return T
	def run(self, x):
		S = self.deltastar(self.s, x)
		return (S&self.F) != set()
	def toDFT(self):
		Q = set()
		delta = {}
		s = frozenset([self.s])
		Q.add(s)
		tocons = [s]
		while len(tocons) > 0:
			S = tocons.pop(0)
			for c in Sigma:
				T = set()
				for p in S:
					T |= self.deltastar(p,c)
				if T == set():
					continue
				T = frozenset(T)
				delta[S,c] = T
				if T not in Q:
					Q.add(T)
					tocons.append(T)
		F = set()
		for S in Q:
			if S&self.F != set():
				F.add(S)
		return DFT(Q,s,F,delta)
		


class ENFT(FT):
	def __init__(self, Q, s, f, delta):
		self.Q = Q
		self.s = s
		self.f = f
		self.delta = delta
		self.S = self.Eclosure(set([self.s]))
	def restart(self):
		self.S = self.Eclosure(set([self.s]))
	def step(self, a):
		T = set()
		for p in self.S:
			T |= self.delta.get((p,a), set())
		self.S = self.Eclosure(T)
	def isMatch(self):
		return self.f in self.S
	def isCont(self):
		return self.S != set()
	def eclosure(self, p):
		toclose = [p]
		S = set([p])
		while len(toclose) > 0:
			q = toclose.pop(0)
			T = self.delta.get((q,''), set())
			toclose.extend(T-S)
			S |= T
		return S
	def Eclosure(self, S):
		T = set()
		for p in S:
			T |= self.eclosure(p)
		return T
	def deltastar(self, p, x):
		S = self.eclosure(p)
		for c in x:
			T = set()
			for q in S:
				T |= self.delta.get((q,c), set())
			S = self.Eclosure(T)
		return S
	def run(self, x):
		S = self.deltastar(self.s, x)
		return self.f in S
	def toNFT(self):
		F = set([self.f])
		s = self.s
		Q = self.Q
		if self.f in self.eclosure(self.s):
			F.add(self.s)
		delta = {}
		for q in Q:
			for c in Sigma:
				S = self.deltastar(q,c)
				if S != set():
					delta[q,c] = S
		return NFT(Q, s, F, delta)

r = Cat([Kleene(Alt([Sym('a'), Sym('b')])), Sym('b'), Sym('a')])
m = r.toENFT()
n = m.toNFT()
o = n.toDFT()
p = o.minimize()
