/*  tables.c  */

#include <ctype.h>
#include <strings.h>
#include "globals.h"
#include "rules.h"
#include "tokensets.h"
#include "lalr.h"
#include "storage.h"

#define SUFFIX                  ".tbl"

static int ntokens, nrules, nstates;
static int int_ntokens;
static TOKEN_SET outnumbers, derivable_tokens;
static FILE *tblfile;
static short *tnummap;          /*  map internal -> output#  */
static TOKEN *onummap;          /*  map output# -> token     */
static ITEMPTR *actions;        /*  parser actions vs token#  */
static TOKEN end_of_input;
static BOOL conflict, goaldefault;


static void write_tokens() {
    register TOKEN t;
    register int n;

    for( n=0;  n < ntokens;  n++ ) {
        t = onummap[n];
        if (t == NULLTOKEN)
            (void)fprintf(tblfile, "0  <Dummy %d> \n", n);
        else {
            if (t->kind == NOT_ON_LHS)
                (void)putc( '0', tblfile );
            else if (t->kind != TERMINAL)
                (void)putc( '1', tblfile );
            else
                (void)putc( '2', tblfile );
            (void)fprintf(tblfile, " %s\n",
                SPECIAL_TOKEN(t)? " *EOF* " : t->tokenname );
        }
    }
}


static void write_rules() {
    register RULE r;
    register TOKEN *tp;

    foreach_rule( r ) {
        if (r->rulenum >= nrules) break;
        (void)fprintf(tblfile, "%d %d",
                tnummap[r->lhs->tokennum], r->rhslen);
        for( tp = r->rhs;  *tp != NULLTOKEN;  tp++ )
            (void)fprintf(tblfile, " %d", tnummap[(*tp)->tokennum]);
        (void)putc( '\n', tblfile );
    }

}


static void shift_reduce_optimize() {
    register STATEPTR sp;
    STATEPTR first_normal_state, last_normal_state,
             first_reduce_state, last_reduce_state;
    register ITEMPTR ip;
    int newstatenum = 0;

    foreach_state(sp)
        sp->flag = FALSE;

    first_normal_state = last_normal_state = NULLSTATE;
    first_reduce_state = last_reduce_state = NULLSTATE;

    foreach_state( sp ) {
        if (sp->statenum >= nstates) break;
        ip = sp->first_item;
        if (ip->next_item != NULLITEM ||
            ip->shiftsymbol != NULLTOKEN) {
            if (first_normal_state == NULLSTATE)
                first_normal_state = sp;
            else
                last_normal_state->next_state = sp;
            last_normal_state = sp;
            sp->statenum = newstatenum++;
        } else {
            /*  the state contains a single reduce item  */
            sp->flag = TRUE;
            if (first_reduce_state == NULLSTATE)
                first_reduce_state = sp;
            else
                last_reduce_state->next_state = sp;
            last_reduce_state = sp;
        }
    }
    nstates = newstatenum;
    firststate = first_normal_state;
    if (first_reduce_state != NULLSTATE) {
        last_normal_state->next_state = first_reduce_state;
        last_normal_state = last_reduce_state;
    }
    last_normal_state->next_state = sp;
    if (sp == NULLSTATE)
        laststate = last_normal_state;
    for( sp=first_reduce_state;  sp!=NULLSTATE && sp->flag;
            sp = sp->next_state )
        sp->statenum = newstatenum++;
}


static void write_states() {
    register STATEPTR sp;
    register ITEMPTR ip;
    register TOKEN t;
    STATEPTR dest;
    register int tn;
    int cnt;

    conflict = FALSE;
    foreach_state( sp ) {
        if (sp->statenum >= nstates) break;
        for( tn = 0;  tn < int_ntokens;  tn++ )
            actions[tn] = NULLITEM;
        cnt = 0;
        foreach_item( sp, ip ) {
            t = ip->shiftsymbol;
            if (t != NULLTOKEN) {       /* shift action */
                if (SPECIAL_TOKEN(t))           /* eof marker */
                    continue;                   /* ==> no action (halt) */
                tn = t->tokennum;
                if (actions[tn] == NULLITEM) {
                    cnt++;
                    actions[tn] = ip;
                } else
                    if (actions[tn]->shiftstate != ip->shiftstate)
                        conflict = TRUE;
                continue;
            }
            /*  reduce action  */
            foreach_token( t ) {
                /*  non-terminals can't appear in input  */
                if (t->kind == NULLABLE_NT ||
                    t->kind == NON_NULL_NT) continue;
                if (SPECIAL_TOKEN(t) && t != end_of_input)
                    continue;
                tn = t->tokennum;
                if (member_test(ip->context,tn)) {
                    if (actions[tn] == NULLITEM)
                        cnt++;
                    else
                        conflict = TRUE;
                    actions[tn] = ip;
                }
            }
        }

        /*  Output the actions for the current state  */
        (void)fprintf(tblfile, "%d", cnt);
        for( tn=0;  tn < ntokens;  tn++ ) {

            t = onummap[tn];
            if (t == NULLTOKEN) continue;
            ip = actions[t->tokennum];
            if (ip == NULLITEM) continue;

            t = ip->shiftsymbol;
            if (t != NULLTOKEN) {       /* Shift */
                dest = ip->shiftstate;
                if (dest == NULLSTATE)
                    internal_error( "write_states" );
                if (optimize && dest->flag)     /* Shift-Reduce */
                    (void)fprintf(tblfile, " %d *%d", tn,
                        dest->first_item->rule->rulenum);
                else                            /* plain Shift */
                    (void)fprintf(tblfile, " %d S%d",
                        tn, dest->statenum );
            } else                      /* Reduce */
                (void)fprintf(tblfile, " %d R%d",
                        tn, ip->rule->rulenum);
            cnt--;
        }
        putc( '\n', tblfile );
        if (cnt != 0)
            internal_error( "write_states" );
    }
}


static void open_tblfile( tblfilename, mode )
char *tblfilename, *mode;
{
    char fn[128];
    int len = strlen(tblfilename);
    int i;

    (void)strcpy(fn,tblfilename);
    i = strlen(SUFFIX);
    if ( len <= i || strcmp(fn+len-i,SUFFIX) != 0 )
        (void)strcat(fn,SUFFIX);
    tblfile = fopen( fn, mode );
    if (tblfile == NULL)
        perror( fn );
}


/*  Check the grammar for useless non-terminals and
    unreachable productions/non-terminals.
    Returns TRUE if the grammar is OK; FALSE otherwise. */
BOOL check_rules() {
    BOOL heading = FALSE;
    BOOL changed;
    BOOL grammar_OK = TRUE;
    register RULE r;
    register TOKEN t = NULLTOKEN;
    register TOKEN *tp;
    int lhsn;

    if (goalsymbol == NULLTOKEN) {
        /*  search for a suitable goal to use  */
        foreach_rule( r ) {
            if (! SPECIAL_TOKEN( r->lhs ) ) break;
        }
        if (r == NULLRULE) {
            (void)fprintf(stderr, "no grammar rules defined\n");
            return 0;
        }
        goalsymbol = r->lhs;
        cpreset();
        cprintf( "start symbol assumed to be %s\n",
            goalsymbol->tokenname );
        goaldefault = TRUE;
    } else
        goaldefault = FALSE;

    /*  renumber the tokens/rules/states  */
    reachability( FALSE );

    /*  get numbers of accessible tokens/rules/states  */
    get_accessibility_data( &ntokens, &nrules, &nstates );

    if (optimize)
        shift_reduce_optimize();        /* changes `nstates' */

    clear_set( &derivable_tokens );
    foreach_rule( r ) {
        if (r->rulenum < nrules || SPECIAL_TOKEN(r->lhs))
            continue;
        if (!heading) {
            cprintf( "\nWarning: the following symbols are useless \
(can never be used):\n" );
            heading = TRUE;
            grammar_OK = FALSE;
        }
        if (t == r->lhs) continue;
        t = r->lhs;
        cprintf( "  %s", t->tokenname );
        (void)add_element( &derivable_tokens, t->tokennum );
    }
    if (heading)
        cnewline();

    foreach_token( t ) {
        if (t->kind != NON_NULL_NT)
            (void)add_element( &derivable_tokens, t->tokennum );
    }

    do {
        changed = FALSE;
        foreach_rule( r ) {
            if (r->rulenum >= nrules)
                break;
            lhsn = r->lhs->tokennum;
            if ( member_test(derivable_tokens, lhsn) )
                continue;
            for( tp = r->rhs;  *tp != NULLTOKEN;  tp++ ) {
                t = *tp;
                if ( !member_test(derivable_tokens, t->tokennum) )
                    goto NBG;
            }
            (void)add_element(&derivable_tokens,lhsn);
            changed = TRUE;
NBG:        ;
        }
    } while( changed );

    heading = FALSE;
    foreach_token( t ) {
        if ( member_test( derivable_tokens, t->tokennum)
                || SPECIAL_TOKEN(t) )
            continue;
        if (!heading) {
            cprintf( "\nError: the following symbols have \
incomplete definitions:\n" );
            heading = TRUE;
            grammar_OK = FALSE;
        }
        cprintf( "  %s", t->tokenname );
    }
    if (heading)
        cnewline();
    return grammar_OK;
}


void write_tables( tblfilename )
char *tblfilename;
{
    register RULE r;
    register TOKEN t;
    int nextnum, i;
    BOOL gram_OK;

    open_tblfile( tblfilename, "w" );
    if (tblfile == NULL)
        return;

    gram_OK = check_rules();
    if (goalsymbol == NULLTOKEN) return;

    clear_set( &outnumbers );
    actions = (ITEMPTR *)calloc( (unsigned)ntokens, sizeof(*actions) );
    tnummap = (short *)calloc( (unsigned)ntokens, sizeof(*tnummap) );
    int_ntokens = ntokens;
    ntokens = -1;
    foreach_token( t ) {
        if (SPECIAL_TOKEN(t)) continue;
        nextnum = t->outputnum;
        if (nextnum >= 0) {
            if (member_test( outnumbers, nextnum ))
                internal_error( "write_tables" );
            (void)add_element( &outnumbers, nextnum );
            if (nextnum > ntokens)
                ntokens = nextnum;
        }
    }

    nextnum = 0;
    foreach_token( t ) {
        if (SPECIAL_TOKEN(t)) continue;
        if (t->outputnum >= 0) {
            tnummap[t->tokennum] = t->outputnum;
            continue;
        }
        while( member_test( outnumbers, ++nextnum ) )
            ;
        tnummap[t->tokennum] = nextnum;
        t->outputnum = -nextnum;
        (void)add_element( &outnumbers, nextnum );
    }
    if (nextnum > ntokens)
        ntokens = nextnum;
    ntokens++;

    onummap = (TOKEN *)calloc( (unsigned)ntokens, sizeof(*onummap) );
    for( i=0;  i < ntokens;  i++ )
        onummap[i] = NULLTOKEN;
    foreach_token( t ) {
        if (SPECIAL_TOKEN(t)) continue;
        nextnum = t->outputnum;
        if (nextnum < 0) nextnum = -nextnum;
        onummap[nextnum] = t;
    }
    /*  find invented eof symbol  */
    end_of_input = firststate->first_kernel_item->rule->rhs[1];
    onummap[0] = end_of_input;

    (void)fprintf( tblfile, "#VERSION INT-LALR (version %s)\n",
        VERSION_STRING );
    (void)fprintf( tblfile, "%d %d %d\n", ntokens, nrules, nstates );

    write_tokens();
    write_rules();
    if (gram_OK)
        write_states();

    (void)fclose( tblfile );
    (void)free( (char *)tnummap );
    (void)free( (char *)onummap );
    (void)free( (char *)actions );
    if (conflict)
        (void)fprintf(stderr,
            "Warning:  there are LALR conflicts in the parse tables\n");
    if (goaldefault)
        goalsymbol = NULLTOKEN;
}


/*VARARGS4*/
static int checked_read( nitems, format, inp1, inp2, inp3 )
int nitems;  char *format;  int *inp1, *inp2, *inp3;
{
    int k;

    k = fscanf(tblfile, format, inp1, inp2, inp3);
    return (k != nitems);
}


void read_tables( tblfilename )
char *tblfilename;
{
    register TOKEN t;
    RULE newrule;
    TOKEN lhs, *rhsp;
    register int i;
    int tkind, lhsnum, rhslen, tn;
    char tokentext[128], version[128];
    int linenum = 1;
    BOOL badformat = TRUE;

    if (firstrule != NULLRULE) {
        (void)fprintf(stderr,
        "The %%read command cannot be used after rules \
have been defined\n");
        return;
    }
    onummap = NULL;
    open_tblfile( tblfilename, "r" );
    if (tblfile == NULL)
        return;

    (void)fscanf(tblfile, "#VERSION %[^\n]", version);

    if ( checked_read( 3, "%d %d %d",
            &ntokens, &nrules, &nstates ) ) goto QUIT;
    onummap = (TOKEN *)calloc( (unsigned)ntokens, sizeof(*onummap) );

    for( i = 0;  i < ntokens;  i++ ) {
        linenum++;
        if ( checked_read( 1, "%d", &tkind ) ) goto QUIT;
        if ( getc(tblfile) != ' ' ) goto QUIT;
        if ( checked_read( 1, "%[^\n]", (int *)tokentext ) ) goto QUIT;
        if (tokentext[0] != ' ') {
            t = create_token( tokentext );
            if (tkind == 2)     {       /* declared as a terminal */
                t->kind = TERMINAL;
                t->outputnum = i;
            } else
                t->kind = NOT_ON_LHS;
        } else                  /* dummy or EOF token */
            t = NULLTOKEN;
        onummap[i] = t;
    }

    for( i = 0;  i < nrules;  i++ ) {
        linenum++;
        if ( checked_read( 2, "%d %d", &lhsnum, &rhslen ) )
            goto QUIT;
        if (lhsnum <= 0 || lhsnum >= ntokens) goto QUIT;
        lhs = onummap[lhsnum];
        if (lhs->kind == NOT_ON_LHS) {
            lhs->kind = NON_NULL_NT;
            create_super_rule( lhs );
        }

        newrule = obtain_rule( rhslen );
        newrule->rhs[rhslen] = NULLTOKEN;
        newrule->lhs = lhs;
        for( rhsp = newrule->rhs;  rhslen > 0;  rhsp++, rhslen-- ) {
            if ( checked_read( 1, "%d", &tn) ) goto QUIT;
            if (tn <= 0 || tn >= ntokens) goto QUIT;
            *rhsp = onummap[tn];
        }

        addrule( newrule );
        if (i == 0)
            goalsymbol = lhs;
    }
    badformat = FALSE;

QUIT:
    if (badformat)
        (void)fprintf(stderr,
                "Error in parse table file, near line %d\n", linenum);

    if (onummap != NULL) {
        (void)free( (char *)onummap );
        onummap = NULL;
    }
    (void)fclose( tblfile );

}


void init_tables() {
    static BOOL initdone = FALSE;
    if (!initdone) {
        initialize_set( &outnumbers );
        initialize_set( &derivable_tokens );
        initdone = TRUE;
    } else {
        clear_set( &outnumbers );
        clear_set( &derivable_tokens );
    }
}
