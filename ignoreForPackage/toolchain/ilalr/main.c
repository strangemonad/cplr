/*  main.c  */

#include "globals.h"
#include "rules.h"

static void usage() {
    (void)fprintf(stderr,
        "Usage:  %s  [-O] [-b grammarfile]\n", pgmname);
    exit(1);
}

void main( argc, argv )
int argc;  char *argv[];
{
    register int i;
    register char *cp;

    pgmname = argv[0];
    outfilename = NULL;

    for( i = 1;  i < argc;  i++ ) {
        cp = argv[i];

        if (cp[0] == '-') {
            if (cp[1] == 'O') { /* shift-reduce optimization? */
                optimize = !optimize;
                continue;
            }
            if (cp[1] == 'b') { /* batch mode flag */
                i++;
                if (i >= argc) break;
                outfilename = argv[i];
                /* a filename argument */
                curstream = fopen( outfilename, "r" );
                if (curstream != NULL)
                    continue;
                perror( outfilename );
                exit( 1 );
            }
        }
        usage();
    }

    init_storage();
    init_rules();
    init_lalr();
    init_lookahead();
    init_conflicts();
    init_deleterule();
    init_tables();

    if (outfilename == NULL)
        printf( "INT-LALR version %s \t(for help, type: %%help)\n\n",
            VERSION_STRING );
    readinput();

    if (outfilename != NULL)
        write_tables( outfilename );
    exit(0);

}
