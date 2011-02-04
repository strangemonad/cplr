/*  lookahead.c  */

#include "globals.h"
#include "rules.h"
#include "tokensets.h"
#include "lalr.h"
#include "work.h"

static TOKEN_SET new_context;

static void compute_starters( ip )
ITEMPTR ip;
{
    register TOKEN t, *rhsp;

    clear_set( &new_context );
    rhsp = &( (ip->rule)->rhs[ip->pos+1] );
    for(  t = *rhsp++;  t != NULLTOKEN;  t = *rhsp++ ) {
        merge_sets( &new_context, t->starters );
        if ( t->kind != NULLABLE_NT )
            return;
    }
    /*  run off RHS of the rule, .. so we hit this item's context  */
    merge_sets( &new_context, ip->context );
}


static void check_lookaheads( sp )
STATEPTR sp;
{
    register ITEMPTR ip;
    register RULE r;
    ITEMPTR cip, cpp;
    STATEPTR ssp;
    TOKEN t;

    while( not_empty_item_work_list(sp) ) {
        ip = remove_from_item_work_list(sp);
        t = ip->shiftsymbol;
        if (t == NULLTOKEN) continue;

        compute_starters( ip );
        /* locate and check the completion items */
        foreach_rule_with_lhs( t, r ) {
            if (!find_item(sp,r,0,&cip,&cpp))
                internal_error( "check_lookaheads #2" );
            if (test_merge_sets( &(cip->context), new_context ))
                add_to_item_work_list(sp,cip);
        }

        ssp = ip->shiftstate;
        if (ssp == NULLSTATE) continue;

        /* locate corresponding kernel item in shift state */
        if ( ! find_item(ssp,ip->rule,ip->pos+1,&cip,&cpp) )
            internal_error( "check_lookaheads #1" );
        if (test_merge_sets( &(cip->context), ip->context )) {
            add_to_item_work_list(ssp,cip);
            add_to_state_work_list(ssp);
        }
    }
}


/*  This routine assumes that the lookahead sets change only
    by having new elements ADDED to them.  I.e., it is correct
    only after a new rule has been added to the grammar.        */
void compute_lookahead_sets() {
    register STATEPTR sp;
    register ITEMPTR ip;

    /*  This initialization of our work lists is clearly overkill  */
    clear_state_work_list();
    foreach_state( sp ) {
        clear_item_work_list( sp );
        add_to_state_work_list(sp);
        foreach_item( sp, ip )
            add_to_item_work_list( sp, ip );
    }

    while( not_empty_state_work_list() ) {
        sp = remove_from_state_work_list();
        check_lookaheads(sp);
    }
}


/*  Clears all lookahead sets to empty and
    then recomputes them from scratch.  */
void totally_recompute_lookahead() {
    register STATEPTR sp;
    register ITEMPTR ip;

    clear_state_work_list();
    foreach_state( sp ) {
        clear_item_work_list( sp );
        add_to_state_work_list(sp);
        foreach_item( sp, ip ) {
            clear_set( &(ip->context) );
            add_to_item_work_list( sp, ip );
        }
    }

    while( not_empty_state_work_list() ) {
        sp = remove_from_state_work_list();
        check_lookaheads(sp);
    }
}


void init_lookahead() {
    static BOOL initdone = FALSE;
    if (!initdone) {
        initialize_set( &new_context );
        initdone = TRUE;
    } else
        clear_set( &new_context );
}
