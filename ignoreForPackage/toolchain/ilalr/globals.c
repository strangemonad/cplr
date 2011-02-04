/* globals.c */

#include "globals.h"
#include "rules.h"

char *pgmname;
char *outfilename;
FILE *curstream = stdin;

BOOL debug = FALSE;
BOOL optimize = TRUE;

TOKEN goalsymbol = NULLTOKEN;
