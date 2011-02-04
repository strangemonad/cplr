/*  lalr.c  */

#include "globals.h"
#include "rules.h"
#include "tokensets.h"
#include "lalr.h"
#include "work.h"
#include "storage.h"

     
static void complete_state();


STATEPTR firststate = NULLSTATE;
STATEPTR laststate = NULLSTATE;


#define HASHITEM(ip)    ((int)(ip->rule) + (ip->pos)*37)
#define NEXT_DELETED_STATE      next_in_bucket
#define DUPLICATE_STATE         prev_in_bucket

/* new kernels are built in this state */
static STATE new_kernel[1];

/*  duplicate states to remove after a rule deletion  */
static STATEPTR deleted_states = NULLSTATE;


static ITEMPTR alloc_item( r, pos, next )
RULE r;  int pos;  ITEMPTR next;
{
    register ITEMPTR new;
    TOKEN t;

    new = obtain_item();
    new->rule = r;
    new->next_item = next;
    new->next_kernel_item = next;
    new->pos = pos;
    new->shiftstate = NULLSTATE;
    t = r->rhs[pos];
    new->shiftsymbol = t;
    new->in_item_work_list = FALSE;
    clear_set( &(new->context) );
    return new;
}


/*  searches item set of state `sp' for an item <r,pos>;
    if found, *kpp is set to the item and TRUE returned as the
    function result;  if not found, *prevp and *kpp refer to items
    bracketting the insertion point, and FALSE is returned.  */
BOOL find_item(sp, r, pos, kpp, prevp)
STATEPTR sp;  RULE r;  int pos;  ITEMPTR *kpp, *prevp;
{
    register ITEMPTR kp, prev;
    register TOKEN t;

    t = r->rhs[pos];
    prev = NULLITEM;
    foreach_item( sp, kp ) {
        if ((int)(kp->shiftsymbol) > (int)t) goto RPT;
        if ((int)(kp->shiftsymbol) < (int)t) break;
        if ((int)(kp->rule) < (int)(r)) goto RPT;
        if ((int)(kp->rule) > (int)(r)) break;
        if (kp->pos < pos) goto RPT;
        if (kp->pos > pos) break;
        *kpp = kp;
        return TRUE;            /* item in list */
RPT:
        prev = kp;
    }
    /*  item not found  */
    *kpp = kp;  *prevp = prev;
    return FALSE;
}


static BOOL same_kernel( ksp1, ksp2 )
STATEPTR ksp1, ksp2;
{
    register ITEMPTR kip1, kip2;

    kip2 = ksp2->first_kernel_item;
    foreach_kernel_item(ksp1,kip1) {
        if (kip2 == NULLITEM) break;
        if (kip1->rule != kip2->rule) break;
        if (kip1->pos  != kip2->pos ) break;
        kip2 = kip2->next_kernel_item;
    }
    if (kip1 == NULLITEM && kip2 == NULLITEM)
        return TRUE;
    return FALSE;
}


/*  adds item <r,pos> to kernel set of state referenced by sp */
static void add_kernel_item( sp, r, pos )
STATEPTR sp;  RULE r;  int pos;
{
    ITEMPTR kp, prev;
    STATEPTR tempsp1, tempsp2;
    int newbucket, oldhc;

    if (find_item(sp, r, pos, &kp, &prev)) return;
    kp = alloc_item( r, pos, kp );
    add_to_item_work_list( sp, kp );

    if (prev == NULLITEM) {
        sp->first_kernel_item = sp->first_item = kp;
    } else {
        prev->next_kernel_item = prev->next_item = kp;
    }

    oldhc = sp->hashcode;
    sp->hashcode += HASHITEM( kp );

    /* no further work if we are operating on `new_kernel' */
    if (sp == new_kernel) return;

    /* otherwise transfer the state from one hash bucket to another */
     
    tempsp1 = sp->prev_in_bucket;
    tempsp2 = sp->next_in_bucket;
    if (tempsp1 == NULLSTATE)
        khash[ oldhc % NBUCKETS ] = tempsp2;
    else
        tempsp1->next_in_bucket = tempsp2;
    if (tempsp2 != NULLSTATE)
        tempsp2->prev_in_bucket = tempsp1;

    newbucket = sp->hashcode % NBUCKETS;
    tempsp1 = khash[newbucket];
    sp->prev_in_bucket = NULLSTATE;
    sp->next_in_bucket = tempsp1;
    if (tempsp1 != NULLSTATE)
        tempsp1->prev_in_bucket = sp;
    khash[newbucket] = sp;
}


/*  deletes items of form <r,*> from state referenced by sp.    */
static void delete_items( sp, r )
STATEPTR sp;  RULE r;
{
    register ITEMPTR ip;
    ITEMPTR previp, nextip, kernp, prevkp, dummy;
    STATEPTR tempsp1, tempsp2;
    int newbucket, oldhc;
    BOOL changed = FALSE;

    oldhc = sp->hashcode;
    clear_item_work_list(sp);

    previp = prevkp = NULLITEM;
    kernp = sp->first_kernel_item;
    for( ip = sp->first_item;  ip != NULLITEM;  ip = nextip ) {
        nextip = ip->next_item;
        if (ip->rule == r || (ip != kernp &&
            find_item(new_kernel,ip->rule,ip->pos,&dummy,&dummy))) {
            /*  delete this item  */
            changed = TRUE;
            if (ip == kernp) {
                /*  remove the item from the kernel set  */
                kernp = ip->next_kernel_item;
                if (prevkp == NULLITEM)
                    sp->first_kernel_item = kernp;
                else
                    prevkp->next_item = kernp;
                sp->hashcode -= HASHITEM(ip);
            }
            if (previp == NULLITEM)
                sp->first_item = nextip;
            else
                previp->next_item = nextip;
            release_item(ip);
        } else {
            add_to_item_work_list(sp,ip);
            if (ip == kernp) {
                prevkp = ip;
                kernp = ip->next_kernel_item;
            }
            previp = ip;
        }
    }

    if (!changed) return;

    if (sp->first_kernel_item == NULLITEM) {
        /*  This state is clearly dead - remove it from hash table  */
        tempsp1 = sp->next_in_bucket;
        tempsp2 = sp->prev_in_bucket;
        if (tempsp2 == NULLSTATE)
            khash[oldhc%NBUCKETS] = tempsp1;
        else
            tempsp2->next_in_bucket = tempsp1;
        if (tempsp1 != NULLSTATE)
            tempsp1->prev_in_bucket = tempsp2;

        /*  Add it to list of deleted states  */
        sp->NEXT_DELETED_STATE = deleted_states;
        deleted_states = sp;
        sp->DUPLICATE_STATE = NULLSTATE;
        sp->statenum = -1;
        return;
    }

    /*  check if the changed state is now identical
        to some already existing state  */
    for( tempsp1 = khash[ sp->hashcode % NBUCKETS ];
            tempsp1 != NULLSTATE;  tempsp1 = tempsp1->next_in_bucket ) {
        if (tempsp1 == sp) continue;
        if (!same_kernel(sp,tempsp1)) continue;

        /*  the state already exists  */
        if (tempsp1->statenum < 0)
            sp->statenum = tempsp1->statenum;
        else
            sp->statenum = -tempsp1->statenum;

        /*  remove the duplicate state from the hash bucket  */
        tempsp2 = sp->prev_in_bucket;
        if (tempsp2 == NULLSTATE)
             khash[ sp->hashcode % NBUCKETS ] = sp->next_in_bucket;
        else
            tempsp2->next_in_bucket = sp->next_in_bucket;
        if (sp->next_in_bucket != NULLSTATE)
            (sp->next_in_bucket)->prev_in_bucket = tempsp2;

        /*  put it into a list of states to delete  */
        sp->NEXT_DELETED_STATE = deleted_states;
        deleted_states = sp;
        /*  and remember what state it corresponds to  */
        sp->DUPLICATE_STATE = tempsp1;
     
        return;
    }

    complete_state(sp);
    add_to_state_work_list(sp);
     
    if (oldhc == sp->hashcode) return;

    /* transfer the state from one hash bucket to another */
     
    tempsp1 = sp->prev_in_bucket;
    tempsp2 = sp->next_in_bucket;
    if (tempsp1 == NULLSTATE)
        khash[ oldhc % NBUCKETS ] = tempsp2;
    else
        tempsp1->next_in_bucket = tempsp2;
    if (tempsp2 != NULLSTATE)
        tempsp2->prev_in_bucket = tempsp1;

    newbucket = sp->hashcode % NBUCKETS;
    tempsp1 = khash[newbucket];
    sp->prev_in_bucket = NULLSTATE;
    sp->next_in_bucket = tempsp1;
    if (tempsp1 != NULLSTATE)
        tempsp1->prev_in_bucket = sp;
    khash[newbucket] = sp;
}


/*  adds item <r,pos> to completion set of state referenced by sp */
static void add_compl_item( sp, r, pos )
STATEPTR sp;  RULE r;  int pos;
{
    ITEMPTR kp, prev;

    if (find_item(sp, r, pos, &kp, &prev)) return;
    kp = alloc_item( r, pos, kp );
    add_to_item_work_list( sp, kp );

    if (prev == NULLITEM)
        sp->first_item = kp;
    else
        prev->next_item = kp;
}


static void start_new_kernel() {
    bzero( (char *)new_kernel, sizeof(STATE) );
    new_kernel->first_item = NULLITEM;
    new_kernel->first_kernel_item = NULLITEM;
}


/* Checks if a state with the same kernel items as `new_kernel'
   already exists.  If it does, the new_kernel state is cleared,
   *flagp is set to FALSE and the matching state is returned.
   If it doesn't, *flagp is set to TRUE and a new kernel state
   is returned as the function result.                          */
static STATEPTR kernel_state( flagp )
BOOL *flagp;
{
    register STATEPTR ksp;
    int kernel_hash = new_kernel->hashcode;
    STATEPTR *kheadp, ns;
    int statenum;

    kheadp = &( khash[ kernel_hash % NBUCKETS ] );
    for( ksp = *kheadp;  ksp!=NULLSTATE;  ksp=ksp->next_in_bucket ) {
        if (ksp->hashcode == kernel_hash
                && same_kernel(ksp,new_kernel) ) {
            release_item_list( new_kernel );
            bzero( (char *)new_kernel, sizeof(STATE) );
            *flagp = FALSE;
            return ksp;
        }
    }

    ksp = obtain_state();
    statenum = ksp->statenum;
    ns = ksp->next_state;
    bcopy( (char *)new_kernel, (char *)ksp, sizeof(STATE) );
    ksp->statenum = statenum;
    ksp->next_state = ns;
    ksp->hashcode = kernel_hash;
    ksp->next_in_bucket = *kheadp;
    ksp->prev_in_bucket = NULLSTATE;
    if (*kheadp != NULLSTATE)
        (*kheadp)->prev_in_bucket = ksp;
    *kheadp = ksp;

    *flagp = TRUE;
    bzero( (char *)new_kernel, sizeof(STATE) );
    return ksp;
}


#define foreach_state_using(t,s)        \
                        for(s = next_tok_use(t,NULLSTATE); \
                        s != NULLSTATE;  s = next_tok_use(t,s) )

STATEPTR next_tok_use( t, sp )
TOKEN t;  register STATEPTR sp;
{
    register ITEMPTR ip;

    if (sp == NULLSTATE)
        sp = firststate;
    else
        sp = sp->next_state;
    for( ;  sp != NULLSTATE;  sp = sp->next_state ) {
        foreach_item(sp,ip)
            if ( ip->shiftsymbol == t)
                return sp;
    }
    return NULLSTATE;
}


/*  On entry, the item work list for state sp contains one or more
    new items.  Each item is checked and completion items created
    if necessary; each completion item goes into the work list so
    that the process iterates until convergence.                */
static void complete_state( sp )
STATEPTR sp;
{
    register RULE r;
    register TOKEN t;
    register ITEMPTR ip;

    while( not_empty_item_work_list( sp ) ) {
        ip = remove_from_item_work_list( sp );
        t = ip->shiftsymbol;
        if (t == NULLTOKEN || t->kind == TERMINAL ||
                t->kind == NOT_ON_LHS)
            continue;
        foreach_rule_with_lhs(t, r)
            add_compl_item( sp, r, 0 );
    }
}


static void check_transitions( sp )
STATEPTR sp;
{
    register ITEMPTR ip;
    ITEMPTR first_in_group;
    register TOKEN t;
    TOKEN curr_t;
    STATEPTR dsp;
    BOOL newstateflag;

    /*  First pass:  find any shift items that do not have a
        destination state -- obviously new items.  The first
        item for each shift symbol is remembered in the work list */
    clear_item_work_list( sp );
    curr_t = NULLTOKEN;  first_in_group = NULLITEM;
    foreach_item(sp, ip) {
        t = ip->shiftsymbol;
        if (t != curr_t) {
            first_in_group = ip;
            curr_t = t;
        }
        if (t == NULLTOKEN) continue;   /* it was a reduce item */
        if (ip->shiftstate != NULLSTATE) continue;
        add_to_item_work_list( sp, first_in_group );
    }
    /*  Second Pass:  construct kernels by shifting on each
        symbol encountered in new items found in pass 1,
        and check to see if these kernels form new states.  */
    while( not_empty_item_work_list( sp ) ) {
        first_in_group = remove_from_item_work_list( sp );
        curr_t = first_in_group->shiftsymbol;
        start_new_kernel();
        for( ip = first_in_group; ip != NULLITEM &&
                ip->shiftsymbol == curr_t; ip = ip->next_item ) {
            add_kernel_item( new_kernel, ip->rule, ip->pos+1 );
        }
        dsp = kernel_state( &newstateflag );

        /*  redirect transitions (incl. missing ones) to the state  */
        for( ip = first_in_group; ip != NULLITEM &&
                ip->shiftsymbol == curr_t; ip = ip->next_item ) {
            ip->shiftstate = dsp;
        }
        if ( newstateflag ) {
            /* we just created a new state, so it must be completed
               and have its transitions checked too */
            complete_state( dsp );
            add_to_state_work_list( dsp );
        }
    }
}


/*  Update LR recognizer when rule r is deleted  */
void delete_states( r )
RULE r;
{
    register int i;
    register STATEPTR sp;
    register ITEMPTR ip;
    register STATEPTR tp;

    /*  Create the set of all items of form <r,*>
        and their completion items in `new_kernel'  */
    start_new_kernel();
    for( i=0;  i <= r->rhslen;  i++ )
        add_kernel_item( new_kernel, r, i );
    complete_state( new_kernel );

    deleted_states = NULLSTATE;
    clear_state_work_list();

    /*  Remove items from states  */
    foreach_state( sp )
        delete_items( sp, r );

    /*  Dispose of our item set  */
    release_item_list( new_kernel );
    bzero( (char *)new_kernel, sizeof(STATE) );

    /*  Items may have been added back in (and shift items
        will have NULL destination states) - fix these. */
    while( not_empty_state_work_list() ) {
        sp = remove_from_state_work_list();
        check_transitions(sp);
    }

    /*  Remove references to deleted states  */
    foreach_state( sp ) {
        if (sp->statenum < 0) continue;
        foreach_item(sp,ip) {
            tp = ip->shiftstate;
            if (tp == NULLSTATE) {
                if (ip->shiftsymbol != NULLTOKEN)
                    internal_error( "delete_states" );
                continue;
            }
            if (tp->statenum >= 0) continue;
            ip->shiftstate = tp->DUPLICATE_STATE;
        }
    }

    if (deleted_states != NULLSTATE) {
        do {
            sp = deleted_states;
            deleted_states = sp->NEXT_DELETED_STATE;
            sp->statenum = 1;
        } while( deleted_states != NULLSTATE );
        reachability( TRUE );
    }

}


void update_lalr_tables( r )
RULE r;
{
    TOKEN lhs;
    register STATEPTR sp;

    lhs = r->lhs;

    /*  First, we must find all states which accept `lhs' as the
        next symbol -- and add a new completion item to each.
        Each additional item is put into a work list.
        Adding an item may imply the need for yet another
        completion item, so `complete_state' iterates until
        the work list is empty.                                 */

    clear_state_work_list();
    foreach_state_using(lhs,sp) {
        clear_item_work_list( sp );
        add_compl_item( sp, r, 0 );
        complete_state( sp );
        add_to_state_work_list( sp );
    }

    /*  Second, the states that we added items to are now likely
        to be lacking transitions to other states.  These states
        are remembered in a work list, and checked individually by
        `check_transitions' which creates new destination states
        as required.  New states hemselves need checking and are
        therefore added to the work list.                       */

    while( not_empty_state_work_list() ) {
        sp = remove_from_state_work_list();
        check_transitions( sp );
    }

    /*  Next, we recompute the lookahead sets.  Recomputing
        is probably doing too much work, but is easier to
        program for now.                                        */

    compute_lookahead_sets();

    /*  Finally, check if the recognizer has conflicts  */
    check_conflicts();

}


/* t is a newly created token and r is a `super-rule' of the form:
        *S*  ::=  |- t -|
   where `*S*' is the `supergoal'.                              */
void init_for_new_token( t, r )
TOKEN t;  RULE r;
{
    STATEPTR sp1, sp2;
    BOOL flag;

    start_new_kernel();
    add_kernel_item( new_kernel, r, 0 );
    sp1 = t->startstate = kernel_state( &flag );
    start_new_kernel();
    add_kernel_item( new_kernel, r, 1 );
    sp2 = kernel_state( &flag );
    (sp1->first_kernel_item)->shiftstate = sp2;
    start_new_kernel();
    add_kernel_item( new_kernel, r, 2 );
    sp1 = kernel_state( &flag );
    (sp2->first_kernel_item)->shiftstate = sp1;
}


void init_lalr() {
    register int k;

    for( k = 0;  k < NBUCKETS;  k++ )
         khash[k] = NULLSTATE;
    start_new_kernel();
}
