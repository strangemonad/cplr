/*  commands.c  */

#include <stdio.h>
#include <ctype.h>
#include <signal.h>
#include <setjmp.h>
#include "globals.h"
#include "commands.h"


static CMDMAP controls[] = {
    { "start",  CMD_START, " t\t\t- define t as start symbol", 2 },
    { "token",  CMD_TOKEN,
        " t1 [n1] t2 [n2] ... - set token numbers", 2 },
    { "quit",   CMD_QUIT,  "\t\t\t- same as entering ^D", 1 },
    { "delete", CMD_DELETE,
        " lhs n\t\t- delete n-th rule of form:  lhs -> ...", 2 },
    { "print",  CMD_PRINT,
        " tokens\t\t- list the tokens", 1 },
    { "print",  CMD_PRINT,
        " rules\t\t- list the grammar rules", 1 },
    { "print",  CMD_PRINT,
        " rules t\t\t- list all rules with t on the LHS", 1 },
    { "print",  CMD_PRINT,
        " uses t\t\t- list all rules containing t in the RHS", 1 },
    { "print",  CMD_PRINT,
        " null\t\t- list the nullable tokens", 1 },
    { "print",  CMD_PRINT,
        " start\t\t- list the starter sets for tokens", 1 },
    { "print",  CMD_PRINT,
        " states\t\t- list the LALR states", 1 },
    { "print",  CMD_PRINT,
        "\t\t\t- repeat previous form of print command", 1 },
    { "check",  CMD_CHECK,
        "\t\t\t- check the grammar for completeness", 2 },
    { "save",   CMD_SAVE,
        " f\t\t\t- save current grammar in file f", 2 },
    { "include",CMD_INCLUDE, " f\t\t- take input from file f", 2 },
    { "write",  CMD_WRITE, " f\t\t- write parse tables to file f", 2 },
    { "read",   CMD_READ,
        " f\t\t\t- read parse tables from file f", 2 },
    { "comment",CMD_COMMENT,
        " ...\t\t- comment (remainder of line is ignored)", 2 },
    { "clear",  CMD_CLEAR, "\t\t\t- delete all rules and restart", 2 },
    { "help",   CMD_HELP , "\t\t\t- list this help information", 1 },
    { "?",      CMD_HELP , "\t\t\t- same as %help", 1 },
    { NULL,     CMD_NULL , NULL, 0 } };

static jmp_buf env;


static char *preamble[] = {
    "A line with a %% character in the first column is a control",
    "operation.  Other input lines are assumed to be rules to add",
    "to the grammar.  A line of the form:",
    "\tt1  t2  t3  t4 ...",
    "represents the rule:  t1 -> t2 t3 ...",
    "A line of the form:",
    "\t| t2 t3 ...",
    "represents a new rule with the same LHS as the last rule to have",
    "been added.",
    "The control operations (which can all be abbreviated to the first",
    "one or two letters) are:-",
    NULL
};


void print_help() {
    register CMDMAP *cp;
    register char **cpp;

    if (setjmp(env) == 0) {
        redirect_output( sizeof(controls)/sizeof(CMDMAP) +
                sizeof(preamble)/sizeof(char *) + 3 );
        cnewline();
        for( cpp=preamble;  *cpp != NULL;  cpp++ ) {
            cprintf( *cpp );
            cnewline();
        }
        cnewline();
        for( cp = controls;  cp->name != NULL;  cp++ ) {
            cprintf( "\t%%%s%s\n", cp->name, cp->synopsis );
        }
        cnewline();
        redirect_output( -1 );
    }
}


int match( inputstr, fullstr, minlen )
register char *inputstr, *fullstr;  register int minlen;
{
    register int ch;

    for( ; *fullstr != '\0';  minlen-- ) {
        ch = *inputstr++;
        if (ch == '\0' || isspace(ch))
            return minlen <= 0;
        if (ch != *fullstr++)
            return 0;
    }
    return 1;
}


CMDS command_lookup( clpp )
char **clpp;
{
    register CMDMAP *cp;
    register char *clp = *clpp;

    for( cp = controls;  cp->name != NULL;  cp++ ) {
        if ( match( clp, cp->name, cp->len ) ) {
            while( *clp != '\0' && !isspace(*clp) )
                clp++;
            *clpp = clp;
            return cp->cmd;
        }
    }
    return CMD_NULL;
}
