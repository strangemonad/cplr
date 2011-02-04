import adatoken, regular
from regular import Tranexp, Sym, Alt, Cat, Kleene, Opt

from string import lower, upper

def resexp(rw):
	l = []
	for a in rw:
		l += [Alt([Sym(lower(a)), Sym(upper(a))])]
	return Cat(l)
def strexp(s):
	l = []
	for a in s:
		l += [Sym(a)]
	return Cat(l)

resword_str = [
	(adatoken.Abort_RW, 'abort'),
	(adatoken.Declare_RW, 'declare'),
	(adatoken.Generic_RW, 'generic'),
	(adatoken.Of_RW, 'of'),
	(adatoken.Select_RW, 'select'),
	(adatoken.Abs_RW, 'abs'),
	(adatoken.Delay_RW, 'delay'),
	(adatoken.Goto_RW, 'goto'),
	(adatoken.Or_RW, 'or'),
	(adatoken.Separate_RW, 'separate'),
	(adatoken.Accept_RW, 'accept'),
	(adatoken.Delta_RW, 'delta'),
	(adatoken.Others_RW, 'others'),
	(adatoken.Subtype_RW, 'subtype'),
	(adatoken.Access_RW, 'access'),
	(adatoken.Digits_RW, 'digits'),
	(adatoken.If_RW, 'if'),
	(adatoken.Out_RW, 'out'),
	(adatoken.All_RW, 'all'),
	(adatoken.Do_RW, 'do'),
	(adatoken.In_RW, 'in'),
	(adatoken.Task_RW, 'task'),
	(adatoken.And_RW, 'and'),
	(adatoken.Is_RW, 'is'),
	(adatoken.Package_RW, 'package'),
	(adatoken.Terminate_RW, 'terminate'),
	(adatoken.Array_RW, 'array'),
	(adatoken.Pragma_RW, 'pragma'),
	(adatoken.Then_RW, 'then'),
	(adatoken.At_RW, 'at'),
	(adatoken.Else_RW, 'else'),
	(adatoken.Private_RW, 'private'),
	(adatoken.Type_RW, 'type'),
	(adatoken.Elsif_RW, 'elsif'),
	(adatoken.Limited_RW, 'limited'),
	(adatoken.Procedure_RW, 'procedure'),
	(adatoken.End_RW, 'end'),
	(adatoken.Loop_RW, 'loop'),
	(adatoken.Begin_RW, 'begin'),
	(adatoken.Entry_RW, 'entry'),
	(adatoken.Raise_RW, 'raise'),
	(adatoken.Use_RW, 'use'),
	(adatoken.Body_RW, 'body'),
	(adatoken.Exception_RW, 'exception'),
	(adatoken.Range_RW, 'range'),
	(adatoken.Exit_RW, 'exit'),
	(adatoken.Mod_RW, 'mod'),
	(adatoken.Record_RW, 'record'),
	(adatoken.When_RW, 'when'),
	(adatoken.Rem_RW, 'rem'),
	(adatoken.While_RW, 'while'),
	(adatoken.New_RW, 'new'),
	(adatoken.Renames_RW, 'renames'),
	(adatoken.With_RW, 'with'),
	(adatoken.Case_RW, 'case'),
	(adatoken.For_RW, 'for'),
	(adatoken.Not_RW, 'not'),
	(adatoken.Return_RW, 'return'),
	(adatoken.Constant_RW, 'constant'),
	(adatoken.Function_RW, 'function'),
	(adatoken.Null_RW, 'null'),
	(adatoken.Reverse_RW, 'reverse'),
	(adatoken.Xor_RW, 'xor')
]

simple_str = [
	(adatoken.Exponentiate, '**'),
	(adatoken.Multiply, '*'),
	(adatoken.Divide, '\\'),
	(adatoken.Plus, '+'),
	(adatoken.Minus, '-'),
	(adatoken.Ampersand, '&'),
	(adatoken.Equal, '='),
	(adatoken.Not_equal, '/='),
	(adatoken.Less_than, '<'),
	(adatoken.Greater_than, '>'),
	(adatoken.Less_than_or_equal, '<='),
	(adatoken.Greater_than_or_equal, '<='),
	(adatoken.Tick, "'"),
	(adatoken.Double_dot, '..'),
	(adatoken.Colon, ':'),
	(adatoken.Semicolon, ';'),
	(adatoken.Comma, ','),
	(adatoken.Dot, '.'),
	(adatoken.Bar, '|'),
	(adatoken.Left_paren, '('),
	(adatoken.Right_paren, ')'),
	(adatoken.Becomes, ':='),
	(adatoken.Box, '<>'),
	(adatoken.Arrow, '=>')
]

resword_def = [(t,resexp(e)) for (t,e) in resword_str]
simple_def = [(t,strexp(s)) for (t,s) in simple_str]

ascii_set = set([chr(i) for i in range(0, 255)])
uppercaseletter = regular.Alt([regular.Sym(chr(i)) for i in range(ord('A'),ord('Z')+1)])
lowercaseletter = regular.Alt([regular.Sym(chr(i)) for i in range(ord('a'),ord('z')+1)])
digit = regular.Alt([regular.Sym(chr(i)) for i in range(ord('0'),ord('9')+1)])
letter = regular.Alt([uppercaseletter, lowercaseletter])
letterdigit = regular.Alt([letter, digit])
optunderscore = regular.Opt(regular.Sym('_'))
integer = Cat([digit, Kleene(Cat([optunderscore, digit]))])
exponent = Cat([Alt([Sym('E'), Sym('e')]), Opt(Alt([Sym('+'), Sym('-')])), integer])
whitespace = Alt([Sym(chr(i)) for i in [ord(' '), ord('\t'), ord('\n')]]) # incomplete ... look in LRM
noteol = Alt([Sym(a) for a in (ascii_set - set(['\n']))])

identifier = regular.Cat([letter, regular.Kleene(regular.Cat([optunderscore, letterdigit]))])
integerliteral = integer
floatliteral = Cat([integer, Opt(Cat([Sym('.'), integer])), Opt(exponent)])
comment = Cat([Sym('-'), Sym('-'), Kleene(noteol)])

identifier_def = (adatoken.Identifier, identifier)
integer_literal_def = (adatoken.Integer_literal, integerliteral)
float_literal_def = (adatoken.Float_literal, floatliteral)
whitespace_def = (None, whitespace)
comment_def = (None, comment)
complex_def = [
	identifier_def,
	whitespace_def,
	float_literal_def,
	integer_literal_def,
	comment_def
]

# Bah! order matters, rw last
tokendefs = complex_def + simple_def + resword_def


#digit_set = set([chr(i) for i in range(ord('0'), ord('9')+1)])
#letter_set = set([chr(i) for i in range(ord('a'), ord('z')+1)+range(ord('A'), ord('Z')+1)])
#format_effector_set = set([chr(i) for i in [9, 11, 13, 10, 12]]) # LRM 2.1 (e)
#upper_case_letter_set = set([chr(i) for i in range(ord('A'),ord('Z')+1)])
#lower_case_letter_set = set([chr(i) for i in range(ord('a'),ord('z')+1)])
#
#upper_case_letter = Alt([Sym(c) for c in upper_case_letter_set])
#lower_case_letter = Alt([Sym(c) for c in lower_case_letter_set])
#digit = Alt([Sym(chr(i)) for i in range(ord('0'), ord('9')+1)])
#
#epsilon = Sym('')
#BOF = Sym(chr(2))
#EOF = Sym(chr(3))
#letter = Alt([Sym(chr(i)) for i in range(ord('a'), ord('z')+1)+range(ord('A'), ord('Z')+1)])
#letter_or_digit = Alt([letter, digit])
#underscore = Sym('_')
#opt_underscore = Alt([underscore, epsilon])
#dqoute = Sym('"')
#
#number = Cat([digit, Kleene(digit)])
#special_character = Alt([Sym(i) for i in """#"&'()*+,-./:;<=>_|"""])
#other_special_character = Alt([Sym(i) for i in """!$%?@[\]^`{}~"""])
#
#
#integer = Cat([digit, Kleene(Cat([opt_underscore, digit]))])
#identifier = Cat([letter, Kleene(Cat([opt_underscore, letter_or_digit]))])
#
#
#
