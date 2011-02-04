# The set of Ada83 tokens that may be produced by an Ada lexer. For more
# details see the Ada lexical specification used to build the Ada lexer.


from compilertools.lex.token import Token, BOF, EOF
from compilertools.lex.token import Comment, Identifier, ReservedWord

# Lexical Additions:

class PutLine(Token): pass

# Delimeters (LRM 2.1):

class Delimeter(Token): pass
      
class Ampersand(Delimeter): pass
class Apostrophe(Delimeter): pass
class ParenL(Delimeter): pass
class ParenR(Delimeter): pass
class Star(Delimeter): pass
class Plus(Delimeter): pass
class Comma(Delimeter): pass
class Hyphen(Delimeter): pass
class Dot(Delimeter): pass
class Slash(Delimeter): pass
class Colon(Delimeter): pass
class SemiColon(Delimeter): pass
class LessThan(Delimeter): pass
class Equal(Delimeter): pass
class GreaterThan(Delimeter): pass
class VerticalBar(Delimeter): pass

# Compound Delimeters (LRM 2.1):

class Arrow(Delimeter): pass
class DoubleDot(Delimeter): pass
class DoubleStar(Delimeter): pass
class Assignment(Delimeter): pass
class Inequality(Delimeter): pass
class GreaterThanOrEqual(Delimeter): pass
class LessThanOrEqual(Delimeter): pass
class LabelBracketL(Delimeter): pass
class LabelBracketR(Delimeter): pass
class Box(Delimeter): pass


# Literals (LRM 2.4 - 2.6)

class Literal(Token): pass
   
class NumericLit(Literal): pass
class CharacterLit(Literal): pass
class StringLit(Literal):
   def __init__(self, startIndex, endIndex, lexeme):
      Token.__init__(self, startIndex, endIndex, lexeme)
      self.value = lexeme[1:-1]


# Ada83 reserved words (LRM 2.9):

class Abort(ReservedWord): pass
class Abs(ReservedWord): pass
class Accept(ReservedWord): pass
class Access(ReservedWord): pass
class All(ReservedWord): pass
class And(ReservedWord): pass
class Array(ReservedWord): pass
class At(ReservedWord): pass
class Begin(ReservedWord): pass
class Body(ReservedWord): pass
class Case(ReservedWord): pass
class Constant(ReservedWord): pass
class Declare(ReservedWord): pass
class Delay(ReservedWord): pass
class Delta(ReservedWord): pass
class Digits(ReservedWord): pass
class Do(ReservedWord): pass
class Else(ReservedWord): pass
class Elsif(ReservedWord): pass
class End(ReservedWord): pass
class Entry(ReservedWord): pass
class Exception(ReservedWord): pass
class Exit(ReservedWord): pass
class For(ReservedWord): pass
class Function(ReservedWord): pass
class Generic(ReservedWord): pass
class Goto(ReservedWord): pass
class If(ReservedWord): pass
class In(ReservedWord): pass
class Is(ReservedWord): pass
class Limited(ReservedWord): pass
class Loop(ReservedWord): pass
class Mod(ReservedWord): pass
class New(ReservedWord): pass
class Not(ReservedWord): pass
class Null(ReservedWord): pass
class Of(ReservedWord): pass
class Or(ReservedWord): pass
class Others(ReservedWord): pass
class Out(ReservedWord): pass
class Package(ReservedWord): pass
class Pragma(ReservedWord): pass
class Private(ReservedWord): pass
class Procedure(ReservedWord): pass
class Raise(ReservedWord): pass
class Range(ReservedWord): pass
class Record(ReservedWord): pass
class Rem(ReservedWord): pass
class Renames(ReservedWord): pass
class Return(ReservedWord): pass
class Reverse(ReservedWord): pass
class Select(ReservedWord): pass
class Separate(ReservedWord): pass
class Subtype(ReservedWord): pass
class Task(ReservedWord): pass
class Terminate(ReservedWord): pass
class Then(ReservedWord): pass
class Type(ReservedWord): pass
class Use(ReservedWord): pass
class When(ReservedWord): pass
class While(ReservedWord): pass
class With(ReservedWord): pass
class Xor(ReservedWord): pass
