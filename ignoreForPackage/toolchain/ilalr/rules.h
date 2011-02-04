/* rules.h */

#include "globals.h"


typedef enum {
                TERMINAL,
                NOT_ON_LHS,
                NULLABLE_NT,    /* definitely nullable */
                NON_NULL_NT     /* definitely not nullable */
            } TOKEN_STATUS;


typedef struct toksubset {
                unsigned long
                        elements[3];    /* 3*32-element set */
                struct toksubset
                        *next;          /* succeeding elements */
            } *SETPTR;


typedef struct {
                int     setsize;        /* max # that could be in set */
                SETPTR  setp;           /* ptr to first 32-bit chunk */
            } TOKEN_SET;


typedef struct tokenstruc {
                struct tokenstruc
                        *nexttoken,
                        *next_in_token_work_list;
                short   tokennum,       /* internal number */
                        outputnum;      /* external number */
                BOOL    flag,           /* used by garbage collector */
                        in_token_work_list;
                TOKEN_STATUS
                        kind;
                char    *tokenname;
                struct statestruc
                        *startstate;
                struct rulestruc        /* first rule which has */
                        *firstdefn;     /* this token on LHS    */
                TOKEN_SET
                        starters;
            } *TOKEN;


typedef struct rulestruc {
                struct rulestruc
                        *nextrule;
                short   rulenum;
                TOKEN   lhs;

                short   rhslen;
                TOKEN   rhs[1];
        } *RULE;

#define EMPTYSET        { -1, 0 }
#define NULLRULE        (RULE)0
#define NULLTOKEN       (TOKEN)0

extern TOKEN firsttoken, lasttoken;
extern TOKEN goalsymbol, supergoal;
extern RULE firstrule, lastrule;

extern void
        readinput(), init_rules(),
        print_lalr(), print_rule(), print_rules(), print_uses(),
        print_tokens(), print_nullability(), print_starters(),
        addrule(), insertrule(),
        update_starters(), init_for_new_token(),
        init_lalr(), update_lalr_tables(),
        reachability(), init_lookahead(),
        compute_lookahead_sets(), totally_recompute_lookahead(),
        check_conflicts(), init_conflicts(),
        deleterule(), delete_states(), init_deleterule();

extern BOOL
        update_nullability(), nullable_rhs();

extern RULE next_use(), next_with_lhs();


#define foreach_token(x)  for( x = firsttoken; x != NULLTOKEN; \
                                x = x->nexttoken )

#define foreach_rule(r)   for( r=firstrule; r!=NULLRULE; r=r->nextrule )

#define foreach_rule_using(t,r) for( r = next_use(t,NULLRULE); \
                r != NULLRULE;  r = next_use(t,r) )

#define foreach_rule_with_lhs(t,r)  for( r = (t)->firstdefn; \
                (r) != NULLRULE && (r)->lhs == (t);  r = (r)->nextrule )

#define SPECIAL_TOKEN(t)        ((t)->tokenname[0] == ' ')
