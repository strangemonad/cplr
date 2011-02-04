class Token(object):
	def __init__(self, begin, end, lexeme):
		self.begin = begin
		self.end = end
		self.lexeme = lexeme
	def __str__(self):
		return '<' + self.__class__.__name__ + ':' \
		+ str(self.begin) + ',' \
		+ str(self.end) + ',' \
		+ self.lexeme + '>'
	def __repr__(self):
		return str(self)

class Integer_literal(Token):
	pass
class Float_literal(Token):
	pass
class String_literal(Token):
	pass
class Character_literal(Token):
	pass
class Identifier(Token):
	pass
class Exponentiate(Token):
	pass
class Multiply(Token):
	pass
class Divide(Token):
	pass
class Plus(Token):
	pass
class Minus(Token):
	pass
class Ampersand(Token):
	pass
class Equal(Token):
	pass
class Not_equal(Token):
	pass
class Less_than(Token):
	pass
class Greater_than(Token):
	pass
class Less_than_or_equal(Token):
	pass
class Greater_than_or_equal(Token):
	pass
class Tick(Token):
	pass
class Double_dot(Token):
	pass
class Colon(Token):
	pass
class Semicolon(Token):
	pass
class Comma(Token):
	pass
class Dot(Token):
	pass
class Bar(Token):
	pass
class Left_paren(Token):
	pass
class Right_paren(Token):
	pass
class Becomes(Token):
	pass
class Box(Token):
	pass
class Arrow(Token):
	pass
class BOF(Token):
	pass
class EOF(Token):
	pass
class Reserved_word(Token):
	pass
class Abort_RW(Reserved_word):
	pass
class Abs_RW(Reserved_word):
	pass
class Accept_RW(Reserved_word):
	pass
class Access_RW(Reserved_word):
	pass
class All_RW(Reserved_word):
	pass
class And_RW(Reserved_word):
	pass
class Array_RW(Reserved_word):
	pass
class At_RW(Reserved_word):
	pass
class Begin_RW(Reserved_word):
	pass
class Body_RW(Reserved_word):
	pass
class Case_RW(Reserved_word):
	pass
class Constant_RW(Reserved_word):
	pass
class Declare_RW(Reserved_word):
	pass
class Delay_RW(Reserved_word):
	pass
class Delta_RW(Reserved_word):
	pass
class Digits_RW(Reserved_word):
	pass
class Do_RW(Reserved_word):
	pass
class Else_RW(Reserved_word):
	pass
class Elsif_RW(Reserved_word):
	pass
class End_RW(Reserved_word):
	pass
class Entry_RW(Reserved_word):
	pass
class Exception_RW(Reserved_word):
	pass
class Exit_RW(Reserved_word):
	pass
class For_RW(Reserved_word):
	pass
class Function_RW(Reserved_word):
	pass
class Generic_RW(Reserved_word):
	pass
class Goto_RW(Reserved_word):
	pass
class If_RW(Reserved_word):
	pass
class In_RW(Reserved_word):
	pass
class Is_RW(Reserved_word):
	pass
class Limited_RW(Reserved_word):
	pass
class Loop_RW(Reserved_word):
	pass
class Mod_RW(Reserved_word):
	pass
class New_RW(Reserved_word):
	pass
class Not_RW(Reserved_word):
	pass
class Null_RW(Reserved_word):
	pass
class Of_RW(Reserved_word):
	pass
class Or_RW(Reserved_word):
	pass
class Others_RW(Reserved_word):
	pass
class Out_RW(Reserved_word):
	pass
class Package_RW(Reserved_word):
	pass
class Pragma_RW(Reserved_word):
	pass
class Private_RW(Reserved_word):
	pass
class Procedure_RW(Reserved_word):
	pass
class Raise_RW(Reserved_word):
	pass
class Range_RW(Reserved_word):
	pass
class Record_RW(Reserved_word):
	pass
class Rem_RW(Reserved_word):
	pass
class Renames_RW(Reserved_word):
	pass
class Return_RW(Reserved_word):
	pass
class Reverse_RW(Reserved_word):
	pass
class Select_RW(Reserved_word):
	pass
class Separate_RW(Reserved_word):
	pass
class Subtype_RW(Reserved_word):
	pass
class Task_RW(Reserved_word):
	pass
class Terminate_RW(Reserved_word):
	pass
class Then_RW(Reserved_word):
	pass
class Type_RW(Reserved_word):
	pass
class Use_RW(Reserved_word):
	pass
class When_RW(Reserved_word):
	pass
class While_RW(Reserved_word):
	pass
class With_RW(Reserved_word):
	pass
class Xor_RW(Reserved_word):
	pass
