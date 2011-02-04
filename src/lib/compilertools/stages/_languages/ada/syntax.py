
# XXX docs: pragmas (LRM 2.8) and replacement characters (LRM 2.10) are not
# supported. Line ends that aren't represented by a format effecter character
# in the source's byte stream will not be considered as a line ending.

# This file needs to be treated with caution. By default Python guarantees
# that all source files will be interpreted as ASCII. Ada83 source files must
# be encoded as ISO 646. ASCII code points are compatible for the character
# ranges permissible in Ada83 sources. As long as this file is interpreted as
# ASCII or an encoding that is reverse compatible with ASCII Ada sources will
# be properly recognized (Python language reference - 2.4.1 String literals).

# XXX doc Right now we don't support character substitution LRM section 2.10. I
# don't think we are even planning on it.

# XXX TODO. naming this file syntax is a little missleading.


from os import path

from util import persist

from lang.reg.dfa import match, matchIgnoreCase
from lang.reg.epsilon_nfa import alt, concat, epsilon, kleene, string, symbol

from compilertools import scanner
import tokens


# The public API for the module is very simple - there is only one method that
# returns the Ada83 lexical specification as a list of (DFA X Token) pairs.

def definition():
   return persist.loadOrCreate(_makeDefinition, _picklePath("lexicalSpec"))


# The lexical specification is broken up into multiple parts in the remainder
# of this module. Specifying each type of lexical element separately is useful
# mainly for clarity of expression. The DFA conversion can have an exponential
# time worst case. Breaking apart the specification allows each set of DFAs to
# be built and persisted to disk independently. For example, changing the set
# of reserved words, as was done when moving from Ada83 to Ada95 doesn't
# require re-building all the other DFAs.
#
# The following factory method combines the partial specifications in a way
# that's suitable for a longest match parser. Priority is given by the order
# of the elements. In particular, the reserved words are all valid identifiers
# so priority must be given to the reserved word token rather than an
# identifier token if there is ambiguity.

def _makeDefinition():
   factories = [_whiteSpace,
                _comment, 
                _delimeters,
                _stringLiteral,
                _additions,
                _reservedWords,
                _identifier]
   
   defs = [persist.loadOrCreate(factory, _picklePath(factory.__name__))\
           for factory in factories]
   
   return reduce(tuple.__add__, defs)


# The Ada83 lexical elements are specified in section 2 of the LRM. The
# sections that follow mostly mirror that specification.


# Additions to the Ada83 Lexeme:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# There are certain language features (eg: proper support for Text_IO) that
# require an almost complete implementation of the Ada language to support. On
# the flip side, it's hard to test feature support as they are incrementally
# added without something as primitive as a print statement. Simply hard code
# the language features that would require too much support of the full Ada
# language. The hard coded versions can later be replaced by their correct
# implementations.

def _additions():
   print "Creating additions DFA..."
   return ((matchIgnoreCase("put_line"), tokens.PutLine),)


# Character Set:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The Ada83 character set is specified in section 2.1 of the LRM.

lower_case_letters = frozenset(["a", "b", "c", "d", "e", "f", "g", "h", "i",
                                "j", "k", "l", "m", "n", "o", "p", "q", "r",
                                "s", "t", "u", "v", "w", "x", "y", "z"])
upper_case_letters = frozenset(["A", "B", "C", "D", "E", "F", "G", "H", "I",
                                "J", "K", "L", "M", "N", "O", "P", "Q", "R",
                                "S", "T", "U", "V", "W", "X", "Y", "Z"])
digits = frozenset(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])


# The following is little hard to read in Python set notation.
# The special characters are:
# " # & ' ( ) * + , - . / : ; < = > _ |
#
# The other special characters are: 
# ! $ % ? @ [ \ ] ^ ` { } ~ 

special_chars = frozenset(['"', "#", "&", "'", "(", ")", "*", "+", ",", 
                           "-", ".", "/", ":", ";", "<", "=", ">", "_", 
                           "|"])

other_special_chars = frozenset(["!", "$", "%", "?", "@", "[", "\\", "]", "^", 
                                 "`", "{", "}", "~"])

space = frozenset([" "])
horiz_tab = frozenset(["\t"])

# "Format effectors are the ISO (and ASCII) characters called horizontal
# tabulation, vertical tabulation, carriage return, line feed, and form feed."
# In addition the scanner will mark the end of the input stream with an end of
# file marker.

format_effectors = frozenset(["\t", "\v", "\r", "\n", "\f", scanner.EOFSymbol])

graphic_chars =   lower_case_letters \
                | upper_case_letters \
                | digits \
                | special_chars \
                | space \
                | other_special_chars


# Delimeters:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Section 2.2 of the Ada83 LRM specifies delimeters (among other things).

def _delimeters():
   # XXX TEST - complete but untested.

   print "Creating delimeters DFA..."
   return ((match("&"), tokens.Ampersand),
           (match("'"), tokens.Apostrophe),
           (match("("), tokens.ParenL),
           (match(")"), tokens.ParenR),
           (match("*"), tokens.Star),
           (match("+"), tokens.Plus),
           (match(","), tokens.Comma),
           (match("-"), tokens.Hyphen),
           (match("."), tokens.Dot),
           (match("/"), tokens.Slash),
           (match(":"), tokens.Colon),
           (match(";"), tokens.SemiColon),
           (match("<"), tokens.LessThan),
           (match("="), tokens.Equal),
           (match(">"), tokens.GreaterThan),
           (match("|"), tokens.VerticalBar),

           (match("=>"), tokens.Arrow),
           (match(".."), tokens.DoubleDot),
           (match("**"), tokens.DoubleStar),
           (match(":="), tokens.Assignment),
           (match("/="), tokens.Inequality),
           (match(">="), tokens.GreaterThanOrEqual),
           (match("<="), tokens.LessThanOrEqual),
           (match("<<"), tokens.LabelBracketL),
           (match(">>"), tokens.LabelBracketR),
           (match("<>"), tokens.Box),
   )


# Identifiers:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Identifiers are specified in section 2.3 of the LRM.

def _identifier():
   print "Creating identifier DFA..."

   # XXX TEST untested.
   ident = _letter() & \
           kleene((symbol("_") | epsilon()) & \
                  (_letter() | _digit()))
   return ((ident.toDFA(), tokens.Identifier),)


# Numeric Literals:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Numeric literals are specified in section 2.4 of the LRM.

# XXX TODO - implement lexing of numeric literals


# Character Literals:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Character literals are specified in section 2.5 of the LRM.

# XXX TODO - implement lexing of character literals


# String Literals:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# String literals are specified in section 2.6 of the LRM.

def _stringLiteral():
   print "Creating string literal DFA..."

   # XXX TEST untested.
   # XXX TODO support escaping of the " character.
   strLit = symbol('"') &\
            kleene(reduce(alt, map(symbol, graphic_chars - set(['"'])))) &\
            symbol('"')

   return ((strLit.toDFA(), tokens.StringLit),)


def _comment():
   print "Creating comments DFA..."

   # As defined in the Ada83 LRM section 2.8 and partly in section 2.2 
   notLineEnd = kleene(reduce(alt, map(symbol, graphic_chars | horiz_tab)))
   commentsDFA = (string("--") & notLineEnd & _lineEnd()).toDFA()
   return ((commentsDFA, tokens.Comment),)


# The Ada83 reserved words (LRM 2.9)
def _reservedWords():
   print "Creating reserved words DFA..."
   return ((matchIgnoreCase("abort"), tokens.Abort),
           (matchIgnoreCase("abs"), tokens.Abs),
           (matchIgnoreCase("accept"), tokens.Accept),
           (matchIgnoreCase("access"), tokens.Access),
           (matchIgnoreCase("all"), tokens.All),
           (matchIgnoreCase("and"), tokens.And),
           (matchIgnoreCase("array"), tokens.Array),
           (matchIgnoreCase("at"), tokens.At),

           (matchIgnoreCase("begin"), tokens.Begin),
           (matchIgnoreCase("body"), tokens.Body),

           (matchIgnoreCase("case"), tokens.Case),
           (matchIgnoreCase("constant"), tokens.Constant),

           (matchIgnoreCase("declare"), tokens.Declare),
           (matchIgnoreCase("delay"), tokens.Delay),
           (matchIgnoreCase("delta"), tokens.Delta),
           (matchIgnoreCase("digits"), tokens.Digits),
           (matchIgnoreCase("do"), tokens.Do),

           (matchIgnoreCase("else"), tokens.Else),
           (matchIgnoreCase("elsif"), tokens.Elsif),
           (matchIgnoreCase("end"), tokens.End),
           (matchIgnoreCase("entry"), tokens.Entry),
           (matchIgnoreCase("exception"), tokens.Exception),
           (matchIgnoreCase("exit"), tokens.Exit),

           (matchIgnoreCase("for"), tokens.For),
           (matchIgnoreCase("function"), tokens.Function),

           (matchIgnoreCase("generic"), tokens.Generic),
           (matchIgnoreCase("goto"), tokens.Goto),

           (matchIgnoreCase("if"), tokens.If),
           (matchIgnoreCase("in"), tokens.In),
           (matchIgnoreCase("is"), tokens.Is),

           (matchIgnoreCase("limited"), tokens.Limited),
           (matchIgnoreCase("loop"), tokens.Loop),

           (matchIgnoreCase("mod"), tokens.Mod),

           (matchIgnoreCase("new"), tokens.New),
           (matchIgnoreCase("not"), tokens.Not),
           (matchIgnoreCase("null"), tokens.Null),

           (matchIgnoreCase("of"), tokens.Of),
           (matchIgnoreCase("or"), tokens.Or),
           (matchIgnoreCase("others"), tokens.Others),
           (matchIgnoreCase("out"), tokens.Out),

           (matchIgnoreCase("package"), tokens.Package),
           (matchIgnoreCase("pragma"), tokens.Pragma),
           (matchIgnoreCase("private"), tokens.Private),
           (matchIgnoreCase("procedure"), tokens.Procedure),

           (matchIgnoreCase("raise"), tokens.Raise),
           (matchIgnoreCase("range"), tokens.Range),
           (matchIgnoreCase("record"), tokens.Record),
           (matchIgnoreCase("rem"), tokens.Rem),
           (matchIgnoreCase("renames"), tokens.Renames),
           (matchIgnoreCase("return"), tokens.Return),
           (matchIgnoreCase("reverse"), tokens.Reverse),

           (matchIgnoreCase("select"), tokens.Select),
           (matchIgnoreCase("separate"), tokens.Separate),
           (matchIgnoreCase("subtype"), tokens.Subtype),

           (matchIgnoreCase("task"), tokens.Task),
           (matchIgnoreCase("terminate"), tokens.Terminate),
           (matchIgnoreCase("then"), tokens.Then),
           (matchIgnoreCase("type"), tokens.Type),

           (matchIgnoreCase("use"), tokens.Use),

           (matchIgnoreCase("when"), tokens.When),
           (matchIgnoreCase("while"), tokens.While),
           (matchIgnoreCase("with"), tokens.With),

           (matchIgnoreCase("xor"), tokens.Xor))


# XXX move to section corresponding to 2.2
def _whiteSpace():
  print "Creating white space DFA..."

  # This definition is a little missleading when compared to the Ada83 LRM 
  # section 2.2. Section 2.2 is rather confusing in general. White space will 
  # be used as a catch all to eat tokens that aren't graphical. All graphical
  # characters must correspond to some *other* token. Where white space acts as
  # a delimiter or separator it will be included in the definition of the DFA
  # that recognizes that token type.
  whiteSpaceDFA = reduce(alt, map(symbol, space | format_effectors)).toDFA()
  return ((whiteSpaceDFA, None),)



# Lexical Specification Helper Functions:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# There are a few basic epsilon-NFA building blocks that are re-used throughout
# the lexical specification. The functions must build a new epsilon-NFA every
# time since they are used to build larger epsilon-NFAs, which is a
# destructive operation.

def _letter():
   return reduce(alt, map(symbol, lower_case_letters | upper_case_letters))

def _digit():
   return reduce(alt, map(symbol, digits))

def _lineEnd():
   return reduce(alt, map(symbol, format_effectors - horiz_tab))


# The location where each partial recognizer specification is persisted is
# abstracted away.

def _picklePath(name):
   return path.join(path.dirname(__file__), name + ".pkl")
   