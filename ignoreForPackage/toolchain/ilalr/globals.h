#ifndef GLOBALS
#define GLOBALS

#include <stdio.h>
#include <stdlib.h>
#include <strings.h>

#define VERSION_STRING          "1.0"

#define FALSE   0
#define TRUE    1
#define BOOL    char

extern char *outfilename;       /* output grammar file */
extern char *pgmname;           /* name of the executable program */
extern void internal_error();   /* generic abort routine */
extern FILE *curstream;         /* current input stream */
extern void cprintf(),          /* columnated message routine */
        cpreset(),              /* column number reset */
        cnewline(),             /* columnated new line */
        redirect_output();      /* pager control for cprintf */

extern BOOL debug;              /* debug flag */
extern BOOL optimize;           /* shift-reduce optimizations */

#endif
