/*  conflicts.c  */

#include "globals.h"
#include "rules.h"
#include "tokensets.h"
#include "lalr.h"
#include "work.h"


BOOL bad_state;
static TOKEN_SET action_symbols;
static FILE *ttystream = NULL;
static TOKEN_SET terminals;


static BOOL prompt( msg )
char *msg;
{
    char line[256];

    if (ttystream == NULL) {
        ttystream = fopen( "/dev/tty", "r" );
        if (ttystream == NULL) {
            perror( "/dev/tty" );
            exit(1);
        }
    }
    for( ; ; ) {
        (void)fprintf(stderr, "\n%s  (y or n)  ", msg);
        (void)fgets( line, sizeof(line), ttystream );
        if (line[0] == 'y' || line[0] == 'Y') return TRUE;
        if (line[0] == 'n' || line[0] == 'N') return FALSE;
    }
    /*NOTREACHED*/
}


static void find_path( dp )
STATEPTR dp;
{
    register STATEPTR sp;
    register ITEMPTR ip;

    dp->in_state_work_list = TRUE;
    foreach_state( sp ) {
        if (sp->in_state_work_list) continue;
        foreach_item(sp,ip) {
            if (ip->shiftstate == dp) { /* bingo */
                find_path(sp);
                cprintf( " %s", ip->shiftsymbol->tokenname );
                goto RET;
            }
        }
    }
    /* end of the line -- must be at a start state */
RET:
    dp->in_state_work_list = FALSE;
}


static void describe_conflict( sp, ip1, ip2, tok )
STATEPTR sp;  ITEMPTR ip1, ip2;  TOKEN tok;
{
    ITEMPTR ip3;

    cprintf( "A sentential form that cannot be parsed is:\n" );
    find_path( sp );
    cnewline();
    if (ip2->shiftsymbol != NULLTOKEN) {
        ip3 = ip2;  ip2 = ip1;  ip1 = ip3;
    }
    /*  now ip2 cannot be a shift item  */
    cprintf(
        "\nTwo possibilities when the symbol %s is seen next are:\n",
        tok->tokenname );
    if (ip1->shiftsymbol != NULLTOKEN)
        cprintf( "\tshift the symbol" );
    else {
        cprintf( "\treduce by the rule:  " );
        print_rule( ip1->rule );
    }
    cprintf( "\nand     reduce by the rule:  " );
    print_rule( ip2->rule );
    cnewline();
}


static BOOL check_for_conflict( sp )
STATEPTR sp;
{
    TOKEN t;
    register ITEMPTR ip;
    ITEMPTR ip2;
    static char *another =
        "Do you wish to see another conflict in this parser state?";
    BOOL conf = FALSE;

    clear_set( &action_symbols );
    foreach_item( sp, ip ) {
        t = ip->shiftsymbol;
        if ( t != NULLTOKEN ) {         /*  it's a shift item  */
            (void)add_element( &action_symbols, t->tokennum );
            continue;
        }
        /*  it's a reduce item  */
        if ( ! disjoint( action_symbols, ip->context, terminals ) ) {
            if (conf) {
                if (!prompt(another)) return TRUE;
            } else
                cprintf(
                    "\n!! Parser conflict detected (LALR state %d)\n",
                    sp->statenum );
            /*  find any token in the set intersection  */
            foreach_token( t ) {
                if (member_test(action_symbols,t->tokennum) &&
                    member_test(ip->context,t->tokennum) &&
                    member_test(terminals,t->tokennum)) break;
            }
            /*  find one of the conflicting items  */
            foreach_item( sp, ip2 ) {
                if (ip2->shiftsymbol == t &&
                        ip->shiftsymbol == NULLTOKEN)
                    break;
                if (ip2->shiftsymbol == NULLTOKEN &&
                        member_test(ip->context,t->tokennum))
                    break;
            }
            if (ip2 == NULLITEM || ip == ip2)
                internal_error( " " );
            describe_conflict(sp,ip,ip2,t);
            conf = TRUE;
        }
        merge_sets( &action_symbols, ip->context );
    }
    return conf;
}


void check_conflicts() {
    register STATEPTR sp;
    register TOKEN t;

    bad_state = FALSE;
    clear_set( &terminals );
    foreach_token( t ) {
        if (t->kind == NOT_ON_LHS || t->kind == TERMINAL)
            (void)add_element( &terminals, t->tokennum );
    }
    foreach_state( sp ) {
        if (check_for_conflict(sp))
            bad_state = TRUE;
    }

}


void init_conflicts() {
    static BOOL initdone = FALSE;
    if (!initdone) {
        initialize_set( &action_symbols );
        initialize_set( &terminals );
        initdone = TRUE;
    } else {
        clear_set( &action_symbols );
        clear_set( &terminals );
    }
}
