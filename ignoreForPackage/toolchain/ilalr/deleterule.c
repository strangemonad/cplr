/*  deleterule.c  */

#include "globals.h"
#include "rules.h"
#include "work.h"
#include "tokensets.h"

static TOKEN_SET nullable_tokens;


/*  On the assumption that relatively few symbols are nullable, we
    mark all nullable symbols that contain `lhs' in their starter
    sets as non-nullable (only these symbols may change their
    nullability).  Then we iterate over just those symbols,
    re-checking their nullability status.  */
static void recompute_nullability( lhs )
TOKEN lhs;
{
    register TOKEN t;
    register RULE r;
    int count;
    register int k;

    clear_set( &nullable_tokens );
    clear_token_work_list();
    count = 0;

    foreach_token( t ) {
        if (t->kind != NULLABLE_NT)
            continue;
        if ( !member_test(t->starters, lhs->tokennum ) )
            continue;
        add_to_token_work_list(t);
        t->kind = NON_NULL_NT;
        count++;
    }

    k = count;
    /*  This code assumes that work lists
        are implemented as QUEUES!!             */
    while( not_empty_token_work_list() ) {
        k--;
        t = remove_from_token_work_list();
        foreach_rule_with_lhs(t,r) {
            if ( nullable_rhs(r) ) {
                t->kind = NULLABLE_NT;
                (void)add_element( &nullable_tokens, t->tokennum );
                k = count;
                goto OUTER;
            }
        }
        add_to_token_work_list( t );
OUTER:
        if (k < 0) break;
    }

}


/*  We reduce all starter sets to an underestimate of their
    true contents after the rule deletion by emptying all starter
     sets that contain the LHS of the deleted rule.     */
static void delete_starters( lhs )
TOKEN lhs;
{
    register TOKEN t;
    foreach_token( t ) {
        if (member_test(t->starters,lhs->tokennum)) {
            clear_set( &(t->starters) );
            (void)add_element( &(t->starters), t->tokennum );
        }
    }
    update_starters( TRUE, NULLRULE );
}


void deleterule( r )
RULE r;
{
    register RULE prevr, nextr;
    RULE superrule = NULLRULE;
    TOKEN lhs;

    /*  unlink the rule from the linked list  */
    prevr = NULLRULE;
    foreach_rule( nextr ) {
        if (nextr == r) break;
        prevr = nextr;
    }
    if (prevr == NULLRULE)
        firstrule = r->nextrule;
    else
        prevr->nextrule = r->nextrule;

    if (r == lastrule)
        lastrule = prevr;

    lhs = r->lhs;
    if (lhs->firstdefn == r) {
        nextr = r->nextrule;
        lhs->firstdefn = (nextr != NULLRULE && nextr->lhs == lhs)?
                nextr : NULLRULE;
    }
    r->nextrule = NULLRULE;

    if (lhs->firstdefn == NULLRULE && lhs != goalsymbol) {
        /*  it is not on any LHS  */
        lhs->kind = NOT_ON_LHS;
        superrule = lhs->startstate->first_kernel_item->rule;

        /*  unlink the super rule from the linked list  */
        foreach_rule( prevr ) {
            if (prevr->nextrule == superrule) {
                prevr->nextrule = superrule->nextrule;
                break;
            }
        }
        /*  and remove the reference to the start state  */
        lhs->startstate = NULLSTATE;
    }

    if ( nullable_rhs(r) )  /*  we have much work to do!  */
        recompute_nullability( lhs );

    /*  next we have to update starter sets  */
    delete_starters( lhs );

    /*  then, we have to recompute the DFA  */
    delete_states( r );

    /*  finally, we recompute context sets  */
    totally_recompute_lookahead();

}


void init_deleterule() {
    static BOOL initdone = FALSE;
    if (!initdone) {
        initialize_set( &nullable_tokens );
        initdone = TRUE;
    } else
        clear_set( &nullable_tokens );
}
