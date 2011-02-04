
from lang.contextfree import Rule

import nodes as n
import tokens as t


def ignoredTokens():
   return [t.Comment]


def definition():
   # XXX might want to take a similar approach as with syntax and have this 
   # produce a push-down automaton. Then have a driver work it's way through a 
   # token stream using the definition.

   grammar = _compilation +\
             _subprogram +\
             _additions
             # packageRules

   return [Rule(*ruleDef) for ruleDef in grammar]


# XXX TODO: handle pragmas at this level so that programs can parse and then
# report an error mentioning we don't support them.
# XXX TODO: handle all 4 types of program units at this level (subprograms, packages, task units and generic units.) Semantic analysis will report an unsupported error for task units and generic units.

   # return Grammar(compilation_rules + 
   #                pack_rules + 
   #                decl_rules + 
   #                tdecl_rules + 
   #                tdef_rules +
   #              expr_rules +
   #              misc_rules)
   # 

# XXX we might need to either name the non terminals the same as the tree node
# class names or simply put the tree node type.

# Compilation rules are specified in section 10 of the Ada83 LRM.

_compilation = [

# A program is a library of program units. Units are added to a program via
# compilation. Zero or more compilation units can be submited to each
# compilation.

   (n.Compilation, (n.SubprogramBody,)),
   
   # (n.Compilation, (n.Compilation, n.CompilationUnit)),
   # (n.Compilation, ()),

# In particular, a compilation unit represents somewhat richer information
# than the program unit alone. It gives the compiler enough context to support
# separate compilation of programs.

   # (n.CompilationUnit, (n.ContextClause, n.LibraryUnit)),
   # XXX TODO - separate compilation
   # (n.CompilationUnit, (n.ContextClause, n.SecondaryUnit)),

   # XXX TODO - support packages
   # (n.LibraryUnit, (n.PackageDecl,))
   # (n.LibraryUnit, (n.SubprogramDecl,)),
   # (n.LibraryUnit, (n.SubprogramBody,)),

   # XXX TODO. stub this out just enough to report an unsupported error.
   # (n.LibraryUnit, (n.GenericDecl,))
   # (n.LibraryUnit, (n.GenericInstantiation,))
   
   # XXX TODO - this is the rest of separate compilation.
   # (n.SecondaryUnit, (n.LibraryUnitBody,))
   # (n.SecondaryUnit, (n.SubUnit,))
   # 
   # (n.LibraryUnitBody, (n.SubprogramBody,))
   # (n.LibraryUnitBody, (n.PackageBody,))
]


# XXX what section are packages specified in? 4?
# XX TODO
# _package = [
#    (n.PackageDecl, (t.Package,)),
#    (n.PackageBody, (t.Identifier,))
# ]


# Subprograms are specified in section 6 of the Ada83 LRM.

_subprogram = [

# Subprograms are one of the four types of program units - the others are
# packages, generics and tasks. Subprograms can take two forms, procedures and
# functions. Subprograms can be defined in two parts, a declaration and a
# body.

   # (n.SubprogramDecl, (n.SubprogramSpec,)),
   
   # XXX only accepts empty bodies. Doesn't handle exceptions. Look at LRM 6.3
   (n.SubprogramBody, (n.SubprogramSpec, t.Is,
                       n.OptSubprogramDeclPart,
                       t.Begin,
                       n.Statements,
                       t.End, n.OptDesignator, t.SemiColon)),
   
   (n.SubprogramSpec, (t.Procedure, t.Identifier)),
   
   # XXX make it just nullable for now.
   (n.OptSubprogramDeclPart, ()),
   (n.Statements, (n.PrintStmt,)),
   (n.OptDesignator, (n.Designator,)),
   (n.OptDesignator, ()),
   
   (n.Designator, (t.Identifier,)),
   (n.Designator, (n.OperatorSymbol,)),


   # XXX see LRM sect. 6 for details on operator  symbols.
   # XXX TEST operator symbols are untested.
   (n.OperatorSymbol, (t.StringLit,)),
]

_additions = [
   (n.PrintStmt, (t.PutLine, t.ParenL, t.StringLit, t.ParenR, t.SemiColon)),
   
]

#  Rule('<packdecl>', (t.Package,
#                      t.Identifier,
#                      t.Is,
#                      '<decls>',
#                      t.End, 
#                      '<id_opt>', 
#                      t.Semicolon)),
#  Rule('<packdecl>', (t.Package,
#                      t.Identifier,
#                      t.Is,
#                      '<decls>',
#                      Private_RW,
#                      '<decls>',
#                      End_RW,
#                      '<id_opt>',
#                      Semicolon)),
# ]
# 

# XXX put the LRM reference for each part.

# subprogram_rules = [
#  Rule('<subprogram_decl>', ('<proc_decl>',)),
#  Rule('<proc_decl>', (Procedure_RW,
#                       Identifier,
#                       '<formal_part_opt>',
#                       Semicolon)),
#  Rule('<formal_part_opt>', (Left_paren,
#                             '<param_specs>',
#                             Right_paren)),
#  Rule('<formal_part_opt>', ()),
#  Rule('<param_specs>', ('<param_specs>',
#                         Semicolon,
#                         '<param_spec>')),
#  Rule('<param_specs>', ('<param_spec>',)),
#  Rule('<param_spec>', ('<identifiers>',
#                        Colon,
#                        '<expression>')),
#  Rule('<mode_opt>', ('<mode>',)),
#  Rule('<mode_opt>', ()),
#  Rule('<mode>', (In_RW,)),
#  Rule('<mode>', (Out_RW,)),
#  Rule('<mode>', (In_RW,
#                  Out_RW)),
#  Rule('<mode>', ())
# ]
# 
# decl_rules = [
#  Rule('<decls>', ('<decls>',
#                   '<decl>'), (addlist, (0,1))),
#  Rule('<decls>', (), (list, ())),
#  Rule('<decl>', ('<obj_decl>',), (id, (0,))),
#  Rule('<decl>', ('<tdecl>',)),
#  Rule('<obj_decl>', ('<ids>',
#                      Colon,
#                      '<const_opt>',
#                      '<expr>',
#                      Semicolon)),
#  Rule('<obj_decl>', ('<ids>',
#                      Colon,
#                      '<const_opt>',
#                      '<expr>',
#                      Becomes,
#                      '<expr>',
#                      Semicolon)),
#  Rule('<const_opt>', (Constant_RW,), (id, (0,))),
#  Rule('<const_opt>', (), (none, ()))
# ]
# 
# tdecl_rules = [
#  Rule('<tdecl>', (Type_RW,
#                  Identifier,
#                  Is_RW,
#                  '<tdef>',
#                  Semicolon)),
# ]
# 
# tdef_rules = [
#  Rule('<tdef>', ('<enum>',)),
#  Rule('<enum>', (Left_paren,
#                  '<ids>',
#                  Right_paren))
# ]
# 
# 
# # XXX come back and complete this.
# # expr_rules = [
# #  Rule('<
# #  Rule('<expr>', (Identifier,), (id, (0,)))
# # ]
# 
# misc_rules = [
#  Rule('<ids>', ('<ids>',
#                 Comma,
#                 Identifier),
#                 (addlist, (0,1))),
#  Rule('<ids>', (Identifier,), (mklist, (0,))),
#  Rule('<id_opt>', (Identifier,)),
#  Rule('<id_opt>', ()),
#  Rule('<init_opt>', (Becomes,
#                      '<expr>')),
#  Rule('<init_opt>', ())
# ]
