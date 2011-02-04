class Scanner(object):
	def __init__(self, tokendefs):
		self.tokendefs = tokendefs
		self.tokenfts = []
		for (t,e) in self.tokendefs:
			self.tokenfts.append((t,e.toENFT()))
	def lex(self, source):
		output = []
		errors = []
		pos = 0
		while pos < len(source):
			(foundmatch, matcht, matchend) = self.longest(source[pos:])
			if foundmatch:
				if matcht != None:
					t = matcht(pos, pos+matchend, source[pos:pos+matchend])
					output.append(t)
				pos += matchend
			else:
				errors.append(pos)
				pos += 1
		return (output,errors)
	def longest(self, source):
		for (t,m) in self.tokenfts:
			m.restart()
		possible = True
		foundmatch = False
		pos = 0
		matchend = 0
		matcht = None
		while possible and (pos < len(source)):
			possible = False
			for (t,m) in self.tokenfts:
				m.step(source[pos])
				possible |= m.isCont()
				foundmatch |= m.isMatch()
				if m.isMatch():
					matchend = pos+1
					matcht = t
			pos += 1
		return (foundmatch, matcht, matchend)
