/*  rules.c  */

#include "globals.h"
#include "rules.h"


TOKEN firsttoken = NULLTOKEN;
TOKEN lasttoken  = NULLTOKEN;
TOKEN supergoal  = NULLTOKEN;
RULE  firstrule  = NULLRULE;
RULE  lastrule   = NULLRULE;


/*  Iterator function for `foreach_rule_using' loop  */
RULE next_use( t, r )
TOKEN t;  register RULE r;
{
    register TOKEN *tp;

    if (r == NULLRULE)
        r = firstrule;
    else
        r = r->nextrule;
    while( r != NULLRULE ) {
        for( tp = &(r->rhs[0]);  (*tp) != NULLTOKEN;  tp++ ) {
            if (*tp == t) return r;
        }
        r = r->nextrule;
    }
    return NULLRULE;
}


void insertrule( r )
RULE r;
{
    TOKEN t = r->lhs;
    register RULE  rr, prev;


    /* find first rule with `t' on LHS */
    rr = t->firstdefn;

    if (rr == NULLRULE) {
        if (firstrule == NULLRULE) {
            lastrule = firstrule = r;
        } else
            lastrule->nextrule = r;
        t->firstdefn = r;
    } else {
        /* find last rule with `t' on LHS */
        while( rr != NULLRULE && rr->lhs == t ) {
            prev = rr;
            rr = rr->nextrule;
        }
        prev->nextrule = r;
    }

    r->nextrule = rr;
    if (rr == NULLRULE)
        lastrule = r;

}


/*  output current set of rules to file `fn'  */
void save_state( fn )
char *fn;
{
    FILE *f;
    register TOKEN t, *rhsp;
    register RULE r;
    char ch;

    f = fopen( fn, "w" );
    if (f == NULL) {
        perror( fn );
        return;
    }

    foreach_token( t ) {
        if (SPECIAL_TOKEN(t)) continue;
        if (t->kind != TERMINAL) continue;
        (void)fprintf(f, "%%token %s", t->tokenname);
        if (t->outputnum > 0)
            (void)fprintf(f, " %d\n", t->outputnum );
        else
            (void)putc( '\n', f );
    }
    if (goalsymbol != NULLTOKEN)
        (void)fprintf(f, "%%start %s\n", goalsymbol->tokenname);

    foreach_rule( r ) {
        t = r->lhs;
        if (SPECIAL_TOKEN(t)) continue;
        (void)fputs( t->tokenname, f );
        ch = '\t';
        for( rhsp = r->rhs;  *rhsp != NULLTOKEN;  rhsp++ ) {
            (void)fprintf(f, "%c%s", ch, (*rhsp)->tokenname );
            ch = ' ';
        }
        (void)putc( '\n', f );
    }

    (void)fclose( f );
}
