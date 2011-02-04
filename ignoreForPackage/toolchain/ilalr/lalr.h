/*  lalr.h  */

typedef struct itemstruc {
                RULE    rule;
                short   pos;
                BOOL    in_item_work_list;
                TOKEN_SET
                        context;
                TOKEN   shiftsymbol;    /* == rule->rhs[pos],       */
                                        /* NULLTOKEN -> reduce item */
                struct statestruc       /* == NULLSTATE if this is  */
                        *shiftstate;    /* a reduce item            */
                struct itemstruc
                        *next_item,
                        *next_kernel_item,
                        *next_in_item_work_list;

            } ITEM, *ITEMPTR;


typedef struct statestruc {
                int     statenum,
                        hashcode;
                BOOL    flag,
                        in_state_work_list;
                ITEMPTR first_item,
                        first_kernel_item,
                        item_work_list_head,
                        item_work_list_tail;
                struct statestruc
                        *next_state,
                        *next_in_bucket,
                        *prev_in_bucket,
                        *next_in_state_work_list;
            } STATE, *STATEPTR;


#define NULLSTATE       (STATEPTR)0
#define NULLITEM        (ITEMPTR)0
#define NBUCKETS        256


extern STATEPTR firststate, laststate;
extern STATEPTR khash[NBUCKETS];

extern BOOL find_item();


#define foreach_state(s)        for( s = firststate;  s != NULLSTATE; \
                                        s = s->next_state )

#define foreach_item(s,i)       for( i = s->first_item; \
                                    i != NULLITEM; i = i->next_item )

#define foreach_kernel_item(s,i)        for( i = s->first_kernel_item; \
                            i != NULLITEM; i = i->next_kernel_item )
