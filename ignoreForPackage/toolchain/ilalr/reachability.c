/*  reachability.c  */

#include "globals.h"
#include "rules.h"
#include "lalr.h"
#include "work.h"
#include "storage.h"


static int ntokens, nrules, nstates;


/*  Marking & garbage collection routine.

    If `remove' == true, unreachable rules/tokens/states are
    deleted; otherwise the unreachable objects are simply moved
    to the ends of the respective object lists.                 */

void reachability( remove )
BOOL  remove;
{
    register ITEMPTR ip;
    register STATEPTR sp;
    register TOKEN t;
    register RULE r;
    STATEPTR ssp, nextsp, deadstates;
    TOKEN prevt, *tp, nextt, deadtokens;
    RULE prevr, nextr, firstdeadrule, lastdeadrule,
        firstgoalrule, lastgoalrule, firstsuperrule, lastsuperrule;
    TOKEN prevgoal = goalsymbol;

    foreach_state( sp )
        sp->flag = FALSE;

    foreach_token( t )
        t->flag = FALSE;

    foreach_rule( r )
        r->rulenum = 0;

    clear_state_work_list();

    if (remove || goalsymbol == NULLTOKEN) {
        goalsymbol = supergoal;
        foreach_token( t ) {
            if (t->kind == TERMINAL || t->kind == NOT_ON_LHS)
                continue;
            sp = t->startstate;
            if (sp == NULLSTATE)
                continue;
            t->flag = TRUE;     /* flag token as in use */
            ip = sp->first_kernel_item;
            r = ip->rule;
            r->rhs[1]->flag = TRUE; /* flag its eof marker as in use */
            add_to_state_work_list( sp );
            sp->flag = TRUE;
        }
    } else {
        sp = goalsymbol->startstate;
        goalsymbol->flag = TRUE;
        ip = sp->first_kernel_item;
        r = ip->rule;
        r->rhs[1]->flag = TRUE; /* flag its eof marker as in use */
        add_to_state_work_list( sp );
        sp->flag = TRUE;
    }

    /*  Visit and mark all reachable states;  simultaneously
        mark any production rules that are used.                */
    while( not_empty_state_work_list() ) {
        sp = remove_from_state_work_list();
        foreach_item( sp, ip ) {
            (ip->rule)->rulenum = -1;
            ssp = ip->shiftstate;
            if (ssp != NULLSTATE && !ssp->flag) {
                add_to_state_work_list(ssp);
                ssp->flag = TRUE;
            }
        }
    }

    /*  Scan through the states - renumber the reachable
        ones, move or de-allocate the unreachable ones. */
    nextstatenum = 1;
    deadstates = ssp = NULLSTATE;
    for( sp = firststate;  sp != NULLSTATE;  sp = nextsp ) {
        nextsp = sp->next_state;
        if (!sp->flag) {
            if (remove)
                release_state(sp);
            else {
                sp->next_state = deadstates;
                deadstates = sp;
            }
            continue;
        }

        /*  force start state to front of list  */
        if (sp == goalsymbol->startstate) {
            sp->next_state = firststate;
            sp->statenum = 0;
            firststate = sp;
            if (ssp == NULLSTATE)
                ssp = sp;
            continue;
        }

        sp->statenum = nextstatenum++;
        if (ssp == NULLSTATE)
            firststate = sp;
        else
            ssp->next_state = sp;
        ssp = sp;
    }

    if (ssp == NULLSTATE)
        firststate = NULLSTATE;
    else
        ssp->next_state = deadstates;

    nstates = nextstatenum;
    for( sp = deadstates; sp != NULLSTATE; sp = sp->next_state ) {
        sp->statenum = nextstatenum++;
        ssp = sp;
    }
    laststate = ssp;

    /*  Scan through the production rules - renumber the
        marked ones, move or de-allocate the unreachable ones.
        Transfer all superrules to end of list.
        Transfer all goal rules to front of list.
        Tokens appearing in marked rules are marked too.        */
    firstgoalrule = firstsuperrule =
        firstdeadrule = prevr = NULLRULE;
    nextrulenum = 0;
    r = firstrule;
    firstrule = NULLRULE;
    for( ;  r != NULLRULE;  r = nextr ) {
        nextr = r->nextrule;
        if (SPECIAL_TOKEN(r->lhs)) {
            if (remove && r->rhs[0]->flag == FALSE) {
                r->rhs[1]->flag = FALSE;        /* this is EOF symbol */
                release_rule( r );
            } else {
                if (firstsuperrule == NULLRULE)
                    firstsuperrule = r;
                else
                    lastsuperrule->nextrule = r;
                lastsuperrule = r;
            }
            continue;
        }
        if (r->rulenum >= 0) {
            if (remove)
                release_rule(r);
            else {
                if (firstdeadrule == NULLRULE)
                    firstdeadrule = r;
                else
                    lastdeadrule->nextrule = r;
                lastdeadrule = r;
            }
            continue;
        }
        if (r->lhs == goalsymbol) {
            if (firstgoalrule == NULLRULE)
                firstgoalrule = r;
            else
                lastgoalrule->nextrule = r;
            lastgoalrule = r;
        } else {
            if (firstrule == NULLRULE)
                firstrule = r;
            else
                prevr->nextrule = r;
            prevr = r;
        }
        r->lhs->flag = TRUE;
        for( tp = &(r->rhs[0]);  *tp != NULLTOKEN;  tp++ )
            (*tp)->flag = TRUE;
    }

    /* insert goal rules at front of list */
    if (firstgoalrule != NULLRULE) {
        lastgoalrule->nextrule = firstrule;
        if (firstrule == NULLRULE)
            prevr = lastgoalrule;
        firstrule = firstgoalrule;
    }

    foreach_rule( r ) {
        r->rulenum = nextrulenum++;
        if (r == prevr) break;
    }

    /* append deadrules to superrules */
    if (firstsuperrule == NULLRULE)
        firstsuperrule = firstdeadrule;
    else
        lastsuperrule->nextrule = firstdeadrule;
    if (firstdeadrule != NULLRULE)
        lastsuperrule = lastdeadrule;

    /* append superrules to live rules */
    if (prevr == NULLRULE)
        firstrule = firstsuperrule;
    else
        prevr->nextrule = firstsuperrule;

    if (firstsuperrule == NULLRULE)
        lastrule = prevr;
    else
        lastrule = lastsuperrule;
    if (lastrule != NULLRULE)
        lastrule->nextrule = NULLRULE;

    nrules = nextrulenum;
    for( r = firstsuperrule; r != NULLRULE; r = r->nextrule )
        r->rulenum = nextrulenum++;

    /*  Our fictitious supergoal cannot be removed  */
    supergoal->flag = TRUE;

    /*  Now scan the tokens */
    ntokens = -1;
    prevt = NULLTOKEN;
    deadtokens = NULLTOKEN;
    for( t = firsttoken;  t != NULLTOKEN;  t = nextt ) {
        nextt = t->nexttoken;
        if (t->flag == FALSE) {
            if (remove)
                release_token( t );
            else {
                t->nexttoken = deadtokens;
                deadtokens = t;
                if (t->tokennum > ntokens)
                    ntokens = t->tokennum;
            }
            continue;
        }
        if (t->tokennum > ntokens)
            ntokens = t->tokennum;
        if (prevt == NULL)
            firsttoken = t;
        else
            prevt->nexttoken = t;
        prevt = t;
    }
    if (prevt == NULL)
        firsttoken = deadtokens;
    else
        prevt->nexttoken = deadtokens;
    ntokens++;
    while( deadtokens != NULLTOKEN ) {
        prevt = deadtokens;
        deadtokens = deadtokens->nexttoken;
    }
    lasttoken = prevt;

    goalsymbol = prevgoal;
}


void get_accessibility_data( pnt, pnr, pns )
int *pnt, *pnr, *pns;
{
    *pnt = ntokens;
    *pnr = nrules;
    *pns = nstates;
}
