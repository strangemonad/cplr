import contextfree

class Node(object):
	def __init__(self,val,kids):
		self.val = val
		self.kids = kids
	def __repr__(self):
		return self.tree2str(0)
	def tree2str(self, l):
		s = (' ' * l) + str(self.val) + '\n'
		for kid in self.kids:
			s += kid.tree2str(l+1)
		return s

class Compilation(Node):
	def __init__(self, units):
		self.units = units
	def tree2str(self, l):
		s = (' '*l) + self.__class__.__name__ + '\n'
		for unit in self.units:
			s += unit.tree2str(l+1)
		return s

class Packdecl(Node):
	def __init__(self, name, decls):
		self.name = name
		self.decls = decls
	def tree2str(self, l):
		s = (' '*l) + self.__class__.__name__ + ':' + '\n'
		s += self.name.tree2str(l+1)
		for decl in self.decls:
			s += decl.tree2str(l+1)
		return s

class Typedecl(Node):
	def __init__(self, name, typedef):
		self.name = name
		self.typedef = typedef
	def tree2str(self,l):
		s = (' '*l) + self.__class__.__name__ + ':' + '\n'
		s += self.name.tree2str(l+1)
		s += self.typedef.tree2str(l+1)
		return s

class Objectdecl(Node):
	def __init__(self, names, constopt, objtype):
		self.names = names
		self.constopt = constopt
		self.objtype = objtype
	def tree2str(self,l):
		s = (' '*l) + self.__class__.__name__ + ':' + '\n'
		for name in self.names:
			s += name.tree2str(l+1)
		if self.constopt != None:
			s += self.constopt.tree2str(l+1)
		s += self.objtype.tree2str(l+1)
		return s
	
		
class Enumdef(Node):
	def __init__(self, enumlits):
		self.enumlits = enumlits
	def tree2str(self,l):
		s = (' '*l) + self.__class__.__name__ + ':' + '\n'
		for enumlit in self.enumlits:
			s += enumlit.tree2str(l+1)
		return s

class Assignment(Node):
	def __init__(self, dest, source):
		self.dest = dest
		self.source = source
	def tree2str(self,l):
		s = (' '*l) + self.__class__.__name__ + ':' + '\n'
		self.dest.tree2str(l+1)
		self.source.tree2str(l+1)
		return s


def select(L, s):
	M = []
	for i in s:
		M.append(L[i])
	return M

def mktree(w):
	S = []
	for a in w:
		if isinstance(a, contextfree.Rule):
			A = a.lhs
			beta = a.rhs
			action = a.action
			kids = S[len(S)-len(beta):len(S)]
			del S[len(S)-len(beta):len(S)]
			if action == None:
				t = Node(A, kids)
			else:
				act, sel = action
				t = act(*select(kids,sel))
			S.append(t)
		else:
			t = Node(a,[])
			S.append(t)
	return S[0]

