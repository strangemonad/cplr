/* starters.c */

#include "globals.h"
#include "rules.h"
#include "tokensets.h"

extern void *malloc();

static void compute_rhs_starters();


/*  if mode==FALSE, we can do a quick update to the starter sets;
    otherwise, we must do a full recomputation.  The code assumes
    that elements are only ever ADDED to starter sets.          */
void update_starters( mode, rule )
BOOL mode;  register RULE rule;
{
    static TOKEN_SET temp_set = EMPTYSET;
    TOKEN  lhs;
    register TOKEN t;
    BOOL   changing;

    if (mode) {         /* perform the full works */
        do {
            changing = FALSE;
            foreach_rule( rule ) {
                compute_rhs_starters( &temp_set, rule );
                changing |=
                    test_merge_sets( &(rule->lhs->starters), temp_set );
            }
        } while( changing );
    } else {            /* quick update */
        lhs = rule->lhs;
        if (rule->rhs[0] != NULLTOKEN) {
            compute_rhs_starters( &temp_set, rule );
            merge_sets( &( lhs->starters ), temp_set );
            foreach_token( t ) {
                if ( t == lhs ||
                        ! member_test( t->starters, lhs->tokennum ) )
                    continue;
                merge_sets( &( t->starters ), lhs->starters );
            }
        }
    }
}


static void compute_rhs_starters( dsp, r )
TOKEN_SET *dsp;  RULE r;
{
    register TOKEN *tp, t;

    clear_set( dsp );
    for( tp = &(r->rhs[0]);  (*tp) != NULLTOKEN;  tp++ ) {
        t = *tp;
        merge_sets( dsp, t->starters );
        if (t->kind != NULLABLE_NT) break;
    }
}
