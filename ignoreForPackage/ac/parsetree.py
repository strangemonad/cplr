import contextfree

class Node(object):
	def __init__(self, val, kids):
		self.val = val
		self.kids = kids
	def __repr__(self):
		return self.tree2str(0)
	def tree2str(self, l):
		s = (' ' * l) + str(self.val) + '\n'
		for kid in self.kids:
			s += kid.tree2str(l+1)
		return s


def mktree(w, G):
	S = []
	for a in w:
		if isinstance(a, contextfree.Rule):
			A = a.lhs
			beta = a.rhs
			kids = S[len(S)-len(beta):len(S)]
			del S[len(S)-len(beta):len(S)]
			t = Node(A, kids)
			S.append(t)
		else:
			t = Node(a, [])
			S.append(t)
	return S[1] # Sp -> |- S -|
