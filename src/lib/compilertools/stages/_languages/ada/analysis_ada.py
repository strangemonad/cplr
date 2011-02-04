""" XXX docs

"""

from util.pipeline import Pipeline

from compilertools import environment
from compilertools.lex.filter import Filter
from compilertools.lex.lexer import LongestMatchLexer
from compilertools.parse import slr
from compilertools.scanner import ByteScanner

import grammar
from symbol_collector import SymbolCollector
from type_constructor import TypeConstructor
import syntax


def makeAnalyzer(env):
   pipeline = Pipeline()

   # XXX make a scanner that also validates the character range accepted by Ada?   
   # XXX only create the phases lazily if they're all needed.
   phases = [("scanner", ByteScanner()),
             ("lexer", LongestMatchLexer(syntax.definition())),
             ("token-filter", Filter(grammar.ignoredTokens())),
             ("parser", slr.Parser(slr.makeGrammar(grammar.definition()))),
             ("type-constructor", TypeConstructor()),
             ("symbol-collector", SymbolCollector()),
   ]

   for phaseName, phase in phases:
      pipeline.append(phase)
      if env.get(environment.LAST_PHASE) == phaseName:
         return (pipeline, False)

   return (pipeline, True)

# XXX TEST: none of this module is tested.
