/*  storage.h  */



extern TOKEN obtain_token(), create_token();
extern RULE  obtain_rule();
extern struct statestruc *  /* STATEPTR */ obtain_state();
extern struct itemstruc  *  /* ITEMPTR  */ obtain_item();

extern void
    release_state(), release_rule(), release_token(),
    release_item(), release_item_list(), set_outputnum();

extern int nextstatenum, nextrulenum;
