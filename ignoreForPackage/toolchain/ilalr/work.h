/*      work.h  */

#ifndef NULLTOKEN
#include "rules.h"
#endif

#ifndef NULLITEM
#include "lalr.h"
#endif

extern BOOL not_empty_token_work_list();
extern void add_to_token_work_list(), clear_token_work_list();
extern TOKEN remove_from_token_work_list();

extern BOOL not_empty_item_work_list();
extern void add_to_item_work_list(), clear_item_work_list();
extern ITEMPTR remove_from_item_work_list();

extern BOOL not_empty_state_work_list();
extern void add_to_state_work_list(), clear_state_work_list();
extern STATEPTR remove_from_state_work_list();
