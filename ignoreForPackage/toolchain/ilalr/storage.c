/*  storage.c  */

#include "globals.h"
#include "rules.h"
#include "lalr.h"
#include "storage.h"
#include "tokensets.h"


static int nexttoknum, nextoutputnum;
int nextrulenum, nextstatenum;

STATEPTR khash[NBUCKETS];


static TOKEN free_tokens;
static ITEMPTR free_items;
static STATEPTR free_states;
static TOKEN_SET outputnums;


TOKEN create_token( name )
char *name;
{
    register TOKEN newt;
    int len = strlen(name) + 1;

    newt = obtain_token();
    newt->tokenname = (char *)malloc( (unsigned)len );
    (void)strcpy( newt->tokenname, name );
    newt->kind = NOT_ON_LHS;
    newt->startstate = NULL;
    newt->next_in_token_work_list = NULLTOKEN;
    newt->in_token_work_list = FALSE;
    clear_set(  &(newt->starters) );
    (void)add_element( &(newt->starters), newt->tokennum );

    return newt;
}


TOKEN obtain_token() {
    register TOKEN newt = free_tokens;

    if (newt != NULLTOKEN)
        free_tokens = newt->nexttoken;
    else {
        newt = (TOKEN)malloc( sizeof(*newt) );
        initialize_set( &(newt->starters) );
        newt->tokennum = nexttoknum++;
    }
     
    newt->outputnum = -1;
    newt->nexttoken = NULLTOKEN;
    newt->firstdefn = NULLRULE;

    /* add token to end of token list */
    if (lasttoken == NULL)
        firsttoken = newt;
    else
        lasttoken->nexttoken = newt;
    lasttoken = newt;

    return newt;
}


void set_outputnum( t, num )
TOKEN t;  int num;
{
    register TOKEN tt;

    if (num == 0) {     /* assign default number */
        while( add_element( &outputnums, nextoutputnum ) == FALSE )
            nextoutputnum++;
        t->outputnum = nextoutputnum++;
        return;
    }
    if ( add_element( &outputnums, num ) != TRUE ) {
        foreach_token( tt ) {
            if (t == tt) continue;
            if (tt->outputnum == num)   /* re-assign the number */
                set_outputnum( tt, 0 );
        }
    }
    t->outputnum = num;
}


RULE obtain_rule( rhslen )
int rhslen;
{
    register RULE newrule;

    newrule = (RULE)malloc( (unsigned)( sizeof(*newrule) +
                        rhslen*sizeof(TOKEN)) );
    newrule->rhslen = rhslen;
    newrule->rulenum = nextrulenum++;
    newrule->nextrule = NULLRULE;
    return newrule;
}


STATEPTR obtain_state() {
    register STATEPTR sp = free_states;

    if (sp != NULLSTATE)
        free_states = sp->next_state;
    else
        sp = (STATEPTR)malloc( sizeof(*sp) );

    sp->statenum = nextstatenum++;
    if (firststate == NULLSTATE)
        firststate = sp;
    else
        laststate->next_state = sp;
    sp->next_state = NULLSTATE;
    laststate = sp;
    sp->first_item = sp->first_kernel_item = NULLITEM;
    sp->hashcode = 0;
    sp->in_state_work_list = FALSE;
    sp->item_work_list_head = NULLITEM;
    sp->item_work_list_tail = NULLITEM;

    return sp;
}


ITEMPTR obtain_item() {
    register ITEMPTR ip = free_items;

    if (ip != NULLITEM)
        free_items = ip->next_item;
    else {
        ip = (ITEMPTR)malloc( sizeof(*ip) );
        initialize_set( &(ip->context) );
    }
    return ip;
}


/*  Releases storage allocated to item ip  */
void release_item( ip )
register ITEMPTR ip;
{
    ip->next_item = free_items;
    free_items = ip;
}


/*  Releases all the items belonging to state sp  */
void release_item_list( sp )
register STATEPTR sp;
{
    register ITEMPTR ip, nip;

    for( ip=sp->first_item;  ip != NULLITEM;  ip = nip ) {
        nip = ip->next_item;
        release_item( ip );
    }
    sp->first_item = sp->first_kernel_item = NULLITEM;
}


/*  Releases storage allocated to state sp and all its items  */
void release_state( sp )
register STATEPTR sp;
{
    register STATEPTR pbcktp, nbcktp;

    nbcktp = sp->next_in_bucket;
    pbcktp = sp->prev_in_bucket;
    if (nbcktp != NULLSTATE)
        nbcktp->prev_in_bucket = pbcktp;
    if (pbcktp != NULLSTATE)
        pbcktp->next_in_bucket = nbcktp;
    else
        khash[ sp->hashcode & NBUCKETS ] = nbcktp;

    release_item_list( sp );
    sp->next_state = free_states;
    free_states = sp;
}


/*  Releases storage allocated to production rule r  */
void release_rule( r )
RULE r;
{
    free( (char *)r );
}


/*  Releases storage allocated to token t  */
void release_token( t )
register TOKEN t;
{
    int tn = t->tokennum;
    register TOKEN tt;
    register ITEMPTR  ip;
    register STATEPTR sp;

    /*  ensure that the deleted token does
        not appear in any token sets            */

    foreach_token( tt )
        if (tt->kind == NON_NULL_NT)
            (void)remove_element( &(tt->starters), tn );

    foreach_state( sp )
        foreach_item( sp, ip )
            (void)remove_element( &(ip->context), tn );

    if (t->outputnum > 0)
        (void)remove_element( &outputnums, t->outputnum );

    t->nexttoken = free_tokens;
    free_tokens = t;
}


void init_storage() {
    static BOOL initdone = FALSE;
    if (!initdone) {
        initialize_set( &outputnums );
        initdone = TRUE;
    } else
        clear_set( &outputnums );
    nexttoknum = 0;
    nextrulenum = 0;
    nextstatenum = 0;
    nextoutputnum = 1;
}


void release_all() {
    register STATEPTR sp;
    register RULE r;
    register TOKEN t;
     
    foreach_state( sp )
        release_state( sp );
    firststate = laststate = NULLSTATE;

    foreach_rule( r )
        release_rule( r );
    firstrule = lastrule = NULLRULE;

    foreach_token( t )
        release_token( t );
    firsttoken = lasttoken = NULLTOKEN;

    supergoal = goalsymbol = NULLTOKEN;
    init_storage();
    init_rules();
    init_conflicts();
    init_deleterule();
    init_lalr();
    init_tables();
}

