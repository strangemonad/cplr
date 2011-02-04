import scanner, adalexis, adatoken
import slr, adagrammar
import parsetree
import sys
import pp
import sbc

print 'creating scanner'
lexer = scanner.Scanner(adalexis.tokendefs)
print 'creating parser'
parser = slr.SLR(adagrammar.G)
parser2 = sbc.SBC(adagrammar.G)

print 'ready for input'
source = sys.stdin.read()
print pp.pp(source)
(tokens, errors) = lexer.lex(source)
tokens.append(adatoken.EOF(len(source), len(source), ''))
tokens[0:0] = [adatoken.BOF(0,0,'')]
print tokens
print errors
errorints = pp.points2ints(errors)
if errorints != []:
	print pp.ppi(source, errorints, True)
	sys.exit(1)
(parse, perrors) = parser2.parse(tokens)
print parse
print perrors
if perrors != []:
	perrors = map((lambda ti: (tokens[ti[0]].begin, tokens[ti[1]].end)), perrors)
	print pp.ppi(source, perrors, True)
	sys.exit(1)
pt = parsetree.mktree(parse[0], adagrammar.G)
print pt
#print parsetree
