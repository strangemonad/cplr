/*      work.c          */

#include "globals.h"
#include "rules.h"
#include "lalr.h"
#include "work.h"


static TOKEN
                token_work_list_head = NULLTOKEN,
                token_work_list_tail = NULLTOKEN;

static STATEPTR
                state_work_list_head = NULLSTATE,
                state_work_list_tail = NULLSTATE;


void clear_token_work_list() {
        while( not_empty_token_work_list() ) {
                (void)remove_from_token_work_list();
        }
        token_work_list_head = token_work_list_tail = NULLTOKEN;
}


void clear_item_work_list( sp )
STATEPTR sp;
{
        while( not_empty_item_work_list( sp ) ) {
                (void)remove_from_item_work_list( sp );
        }
        sp->item_work_list_head = sp->item_work_list_tail = NULLITEM;
}


void clear_state_work_list() {
        while( not_empty_state_work_list() ) {
                (void)remove_from_state_work_list();
        }
        state_work_list_head = state_work_list_tail = NULLSTATE;
}


void add_to_token_work_list( t )
register TOKEN t;
{
    if (t->in_token_work_list)
        return;

    t->next_in_token_work_list = NULLTOKEN;
    t->in_token_work_list = TRUE;
    if (token_work_list_head == NULLTOKEN)
        token_work_list_head = t;
    else
        token_work_list_tail->next_in_token_work_list = t;
    token_work_list_tail = t;
}


void add_to_item_work_list( sp, t )
STATEPTR sp;  register ITEMPTR t;
{
    if (t->in_item_work_list)
        return;

    t->next_in_item_work_list = NULLITEM;
    t->in_item_work_list = TRUE;
    if (sp->item_work_list_head == NULLITEM)
        sp->item_work_list_head = t;
    else
        sp->item_work_list_tail->next_in_item_work_list = t;
    sp->item_work_list_tail = t;
}


void add_to_state_work_list( t )
register STATEPTR t;
{
    if (t->in_state_work_list)
        return;

    t->next_in_state_work_list = NULLSTATE;
    t->in_state_work_list = TRUE;
    if (state_work_list_head == NULLSTATE)
        state_work_list_head = t;
    else
        state_work_list_tail->next_in_state_work_list = t;
    state_work_list_tail = t;
}


TOKEN remove_from_token_work_list() {
    register TOKEN t;

    t = token_work_list_head;
    if (t == NULLTOKEN)
        internal_error("remove_from_token_work_list");
    token_work_list_head = t->next_in_token_work_list;
    t->in_token_work_list = FALSE;
    t->next_in_token_work_list = NULLTOKEN;
    return t;
}


ITEMPTR remove_from_item_work_list( sp )
STATEPTR sp;{
    register ITEMPTR t;
     
    t = sp->item_work_list_head;
    if (t == NULLITEM)
        internal_error("remove_from_item_work_list");
    sp->item_work_list_head = t->next_in_item_work_list;
    t->in_item_work_list = FALSE;
    t->next_in_item_work_list = NULLITEM;
    return t;
}


STATEPTR remove_from_state_work_list() {
    register STATEPTR t;

    t = state_work_list_head;
    if (t == NULLSTATE)
        internal_error("remove_from_state_work_list");
    state_work_list_head = t->next_in_state_work_list;
    t->in_state_work_list = FALSE;
    t->next_in_state_work_list = NULLSTATE;
    return t;
}


BOOL not_empty_token_work_list() {
    return token_work_list_head != NULLTOKEN;
}


BOOL not_empty_item_work_list( sp )
STATEPTR sp;{
    return sp->item_work_list_head != NULLITEM;
}


BOOL not_empty_state_work_list() {
    return state_work_list_head != NULLSTATE;
}
