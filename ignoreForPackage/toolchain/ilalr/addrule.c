/* addrule.c */

#include "globals.h"
#include "rules.h"
#include "work.h"

/*  Test if RHS of rule r is nullable; returning TRUE
    if it is nullable and FALSE if it is non-nullable. */
BOOL nullable_rhs( r )
RULE r;
{
    register TOKEN *tptr;

    for( tptr = &( r->rhs[0] );  (*tptr) != NULLTOKEN;  tptr++ ) {
        if ( (*tptr)->kind != NULLABLE_NT) return FALSE;
    }
    return TRUE;
}


/*  Tests a rule  X -> A B C ...  ;  if X was not previously
    known to be nullable and if all symbols on RHS are nullable,
    the status of X is changed to nullable and X is added to
    the work list.                                              */
static BOOL test_rule( r )
RULE r;
{
    register TOKEN lhs;

    lhs = r->lhs;
    if ( lhs->kind == NULLABLE_NT || !nullable_rhs( r ) )
        return FALSE;
    add_to_token_work_list(lhs);
    lhs->kind = NULLABLE_NT;
    return TRUE;
}


/*  if r is not NULLRULE, r is a newly added rule whose lhs may now
    be nullable.
    Otherwise, the work list contains tokens which are currently
    flagged as non-nullable but this may be incorrect.  In either case,
    the tokens are re-checked for nullability and if a token status is
    changed to nullable, the change is propagated as necessary.       */
BOOL update_nullability( r )
register RULE r;
{
    BOOL status_change = FALSE;
    register TOKEN t;

    clear_token_work_list();
    if ( test_rule( r ) )
        status_change = TRUE;

    /* iterate over all tokens that may become nullable */
    while( not_empty_token_work_list() ) {
        t = remove_from_token_work_list();
        foreach_rule_using(t, r) {
            if ( test_rule( r ) )
                status_change = TRUE;
        }
    }
    return status_change;
}


void addrule( rule )
RULE rule;
{
    TOKEN lhs = rule->lhs;
    BOOL status_change;

    /* a simple credibility check */
    if( lhs->kind == TERMINAL) {
        (void)fprintf(stderr, "LHS of rule (%s) cannot be a terminal\n",
                lhs->tokenname);
        return;
    }

    insertrule( rule );

    status_change = update_nullability( rule );

    update_starters( status_change, rule );

    update_lalr_tables( rule );

}
