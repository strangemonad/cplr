/*  print.c  */

#include "globals.h"
#include "rules.h"
#include "tokensets.h"
#include "lalr.h"
#include <signal.h>
#include <setjmp.h>



#define MAXCOLS         72
#define FEWLINES        10
#define MORE            more    /* the paging program */


static int col = 0;
static FILE *outstream = stdout;
static char *pager = NULL;
static jmp_buf env;
static int (*old_handler)();


int brokenpipe() {
    longjmp( env, 1 );
}


void internal_error( msg )
char *msg;
{
    (void)fprintf( stderr, "!!! Internal Error !!!  (%s)\n", msg );
    abort();
}


/*  The argument is an estimate of how many lines are to be
     output via calls to cprintf.  If the estimate exceeds 10
     or so, the output of cprintf is redirected to `more'.
     A call with an argument of -1 resets the output back to
     normal.                                                    */
void redirect_output( estimate )
int estimate;
{
    FILE *pstream;

    if (estimate < FEWLINES || !isatty(1)) {
        if (outstream != stdout) {
            (void)pclose( outstream );
            (void)signal( SIGPIPE, old_handler );
            (void)fflush(stdin);
        }
        outstream = stdout;
        return;
    }
    if (pager == NULL) {
        pager = getenv( "PAGER" );
        if (pager == NULL) pager = "more";
    }
    pstream = popen( pager, "w" );
    if (pstream == NULL)
        outstream = stdout;
    else {
        outstream = pstream;
        old_handler = signal( SIGPIPE, brokenpipe );
    }
}


/*VARARGS1*/
void cprintf( fmt, arg1, arg2 )
char *fmt, *arg1, *arg2;
{
    char buff[256];
    int len;

    if (ferror(outstream)) return;
    while( *fmt == '\n' ) {
        fmt++;
        putc( '\n', outstream );
        col = 0;
    }
    while( *fmt == '\t' ) {
        fmt++;
        putc( '\t', outstream );
        col = (col + 7) & (-8);
    }
    (void)sprintf( buff, fmt, arg1, arg2 );
    len = strlen( buff );
    col += len;
    if ( col >= MAXCOLS ) {
        fputs( "\n\t", outstream );
        col = 8+len;
    }
    fputs( buff, outstream );
    if ( buff[len-1] == '\n' )
        col = 0;
}


void cpreset() {
    col = 0;
}


void cnewline() {
    col = 0;
    if (!ferror(outstream))
        putc( '\n', outstream );
}


void print_rule( r )
RULE r;
{
    register TOKEN *tptr;

    cprintf( "%s  ::= ", (r->lhs)->tokenname );
    for( tptr = &( r->rhs[0] );  (*tptr) != NULLTOKEN;  tptr++ )
            cprintf( " %s", (*tptr)->tokenname );
    cnewline();
}


void print_rules( lhs )
TOKEN lhs;
{
    RULE r;
    int cnt;

    if (setjmp(env) == 0) {
        if (lhs == NULLTOKEN) {
            cnt = 3;
            foreach_rule( r ) {
                if (!debug && SPECIAL_TOKEN(r->lhs)) continue;
                if (++cnt > FEWLINES) break;
            }
            redirect_output( cnt );
            cnt = 0;
            cprintf( "\nLISTING OF GRAMMAR RULES\n\n" );
            foreach_rule( r ) {
                if (!debug && SPECIAL_TOKEN(r->lhs)) continue;
                cprintf( "%3d:  ", ++cnt );
                print_rule( r );
            }
        } else {
            cnt = 1;
            foreach_rule_with_lhs( lhs, r ) {
                if (++cnt > FEWLINES) break;
            }
            redirect_output( cnt );
            cnt = 0;
            cnewline();
            foreach_rule_with_lhs( lhs, r ) {
                cprintf( "%3d:  ", ++cnt );
                print_rule( r );
            }
        }
        cnewline();
    }
    redirect_output( -1 );
}


void print_tokens() {
    register TOKEN t;
    char *s;
    int  cnt = 3;

    if (setjmp(env) == 0) {
        foreach_token(t) {
            if (!debug && SPECIAL_TOKEN(t)) continue;
            if (++cnt > FEWLINES) break;
        }
        redirect_output( cnt );
        cprintf( "\nLISTING OF TOKENS\n\n" );
        foreach_token( t ) {
            if (!debug && SPECIAL_TOKEN(t)) continue;
            cprintf(  "%s\t", t->tokenname );
            switch( t->kind ) {

            case NOT_ON_LHS:   s = "terminal";                  break;
            case TERMINAL:     s = "terminal";                  break;
            case NON_NULL_NT:  s = "non-terminal (non-nullable)";break;
            case NULLABLE_NT:  s = "non-terminal (nullable)";   break;
            default:
                internal_error( "print_tokens" );

            }
            cprintf( s );
            if (t->outputnum > 0)
                cprintf( ", number = %d", t->outputnum );
            cnewline();
        }
    }
    redirect_output( -1 );
}


/*  prints all rules using `t' anywhere in RHS  */
void print_uses( t )
TOKEN t;
{
    RULE r;
    int cnt = 0;

    if (setjmp(env) == 0) {
        foreach_rule_using(t,r) {
            if (!debug && SPECIAL_TOKEN(r->lhs)) continue;
            if (++cnt > FEWLINES) break;
        }
        if (cnt == 0) {
            cprintf( "Symbol %s is not used in the RHS of any rule\n",
                        t->tokenname );
            return;
        }
        redirect_output( cnt );
        foreach_rule_using( t, r ) {
            if (!debug && SPECIAL_TOKEN(r->lhs)) continue;
            cprintf( "    " );
            print_rule( r );
        }
        cnewline();
    }
    redirect_output( -1 );
}


/*  prints a readable version of set `s', followed by a new-line  */
void print_set( s )
TOKEN_SET s;
{
    register TOKEN t;

    cprintf( "{" );

    foreach_token( t ) {
        if (member_test( s, t->tokennum ))
            cprintf( " %s", t->tokenname );
    }
    cprintf( " }" );
    cnewline();
}


void print_nullability() {
    register TOKEN t;
    BOOL trivial = TRUE;

    foreach_token( t ) {
        if (t->kind != NULLABLE_NT)
            continue;
        if (trivial) {
            trivial = FALSE;
            cprintf( "\nNULLABLE TOKENS:\n" );
        }
        cprintf( " %s", t->tokenname );
    }
    if (trivial)
        cprintf( "\nAll tokens are non-nullable" );
    cnewline();
}


void print_starters() {
    register TOKEN t;
    BOOL trivial = TRUE;

    foreach_token( t ) {
        /*  skip over sets with no interesting members */
        if (cardinality(t->starters) == 1 &&
                member_test( t->starters, t->tokennum ) ) continue;
        if (trivial) {
            trivial = FALSE;
            cprintf( "\nSTARTER SETS\n" );
        }
        cprintf( "%s:  ", t->tokenname );
        print_set(  t->starters );
    }
    if (trivial)
        cprintf( "\nAll starter sets are singletons" );
    cnewline();
}


static void print_item( ip )
register ITEMPTR ip;
{
    RULE r;
    register int i;

    r = ip->rule;
    cprintf( "    [ %s ::= ", r->lhs->tokenname );
    for( i = 0;  i <= r->rhslen;  i++ ) {
        if (i == ip->pos)
            cprintf( " ! " );
        if ( i >= r->rhslen )
            break;
        cprintf( " %s ", (r->rhs[i])->tokenname );
    }
    if (ip->shiftstate != NULLSTATE)
        cprintf( "] --> %d ", ip->shiftstate->statenum );
    else
        cprintf( "] " );
    print_set( ip->context );
}


/* dumps all lalr states to stdout */
void print_lalr() {
    register STATEPTR sp;
    register ITEMPTR kp, ip;
    BOOL cflag;

    if (setjmp( env ) != 0) goto QUIT;
     
    redirect_output( 999 );
    cprintf( "\nLISTING OF LALR(1) STATES\n" );
    foreach_state( sp ) {
        cprintf( "\n** %d **\n", sp->statenum );
        cprintf( "  Kernel items:\n" );
        kp = sp->first_kernel_item;
        cflag = FALSE;
        foreach_item( sp, ip ) {
            if (ip == kp) {
                kp = kp->next_kernel_item;
                print_item( ip );
            } else      /* there is an item not in kernel */
                cflag = TRUE;
        }
        if (!cflag) continue;

        cprintf( "  Completion items:\n" );
        kp = sp->first_kernel_item;
        foreach_item( sp, ip ) {
            if (ip == kp)
                kp = kp->next_kernel_item;
            else        /* item not in kernel */
                print_item( ip );
        }
    }
    cnewline();

QUIT:
    redirect_output( -1 );
}
