def isnewline(c):
	return c == '\n'

tabwidth = 8

def pp(x):
	l = 1
	c = 1
	s = ''
	doline = True
	for i in range(len(x)):
		if doline:
			s += str(l) + ':\t'
			doline = False
		s += x[i]
		if isnewline(x[i]):
			l += 1
			doline = True
	return s

def points2ints(ps):
	ss = []
	while len(ps) > 0:
		q0 = ps.pop(0)
		q1 = q0+1
		while True:
			if len(ps) == 0:
				break
			p = ps[0]
			if p != q1:
				break
			q1 += 1
			ps.pop(0)
		ss.append((q0,q1))
	return ss

def overlap(p,q):
	p0,p1 = p
	q0,q1 = q
	return not (p1 <= q0 or q1 <= p0)
def contains(i,p):
	p0,p1=p
	return (i >=p0 and i < p1)
def intersect(p,q):
	p0,p1 = p
	q0,q1 = q
	return max(p0,q0),min(p1,q1)

def ppi(x, pints = [], ul = False):
	lines = str.splitlines(x,True)
	p = 0
	for i in range(len(lines)):
		q = p + len(lines[i])
		lines[i] = ((p,q), lines[i])
		p = q
	s = ''
	if pints == []:
		pints.append((0,len(x)))
	while len(pints) > 0:
		pint = pints.pop(0)
		p0,p1 = pint
		for i in range(len(lines)):
			lint,l = lines[i]
			(l0,l1) = lint
			if overlap(pint,lint):
				print pint, lint
				qint = intersect(pint,lint)
				q0,q1 = qint
				s += str(i+1) + ':\t' + l
				if ul:
					s += '\t'
					outc = ' '
					col = 0
					for j in range(l0, l1):
						if j == q0:
							c = '|'
						elif j == q1-1:
							c = '|'
						elif contains(j,qint):
							c = '-'
						else:
							c = ' '
						m = 1
						if l[j-l0] == '\t':
							m = tabwidth - col
							col = 0
						else:
							col = (col + 1) % tabwidth
						s += m*c
					s += '\n'
	return s
	
