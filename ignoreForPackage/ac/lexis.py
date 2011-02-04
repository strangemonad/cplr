import adatoken
import regular
import adalexis

tokendefs = adalexis.tokendefs

def longest(source, begin):
	for (t,m) in tokendefs:
		m.restart()
	possible = True
	foundmatch = False
	pos = begin
	matchend = begin
	matcht = None
	while possible and (pos < len(source)):
		possible = False
		for (t,m) in tokendefs:
			m.step(source[pos])
			if m.isCont():
				possible = True
			if m.isMatch():
				foundmatch = True
				matchend = pos+1
				matcht = t
		pos += 1
	if foundmatch:
		return (True, matcht, matchend)
	else:
		return (False, )
def lex(source):
	output = []
	errors = []
	pos = 0
	while pos < len(source):
		r = longest(source, pos)
		if r[0]:
			matcht = r[1]
			matchend = r[2]
			if matcht != None:
				output.append(matcht(pos, matchend, source[pos:matchend]))
			pos = matchend
		else:
			errors.append(pos)
			pos += 1
	return (output,errors)
