/* tokensets.c */

#include "globals.h"
#include "rules.h"
#include "tokensets.h"



/* should be called to initialize storage for the TOKEN_SET type */
void initialize_set( dsp )
TOKEN_SET *dsp;
{
    dsp->setsize = -1;
    dsp->setp = NULL;
}


/* expands storage allocated to set `*dsp' so that it is
   guaranteed to accommodate integer `n' as a member            */
void expand_set( dsp, n )
TOKEN_SET *dsp;  int n;
{
    register SETPTR csp, prev;
     
    if (dsp->setsize >= n) return;
    csp = dsp->setp;
    prev = NULL;
    while( csp != NULL ) {
        prev = csp;  csp = csp->next;
    }
    while( dsp->setsize < n ) {
        csp = (SETPTR)malloc( sizeof(*csp) );
        csp->elements[0] = 0;
        csp->elements[1] = 0;
        csp->elements[2] = 0;
        if (prev == NULL)
            dsp->setp = csp;
        else
            prev->next = csp;
        prev = csp;
        dsp->setsize += 3*32;
    }
    csp->next = NULL;
}


/*  removes all elements from set `dsp'
    (but does not deallocate the storage)       */
void clear_set( dsp )
TOKEN_SET *dsp;
{
    register SETPTR csp;
     
    for( csp = dsp->setp;  csp != NULL;  csp = csp->next ) {
        csp->elements[0] = 0;
        csp->elements[1] = 0;
        csp->elements[2] = 0;
    }
}


/*  adds token `t' into set `dsp';
    the result is TRUE iff the set is changed.  */
BOOL add_element( dsp, tn )
TOKEN_SET *dsp;  int tn;
{
    register SETPTR csp;
    register int bit;

    expand_set( dsp, tn );
    csp = dsp->setp;
    while( tn >= 3*32 ) {
        tn -= 3*32;
        csp = csp->next;
    }
    if (tn < 32) {
        bit = 1 << tn;
        if (csp->elements[0] & bit)
            return FALSE;
        csp->elements[0] |= bit;
    } else
    if (tn < 64) {
        bit = 1 << (tn - 32);
        if (csp->elements[1] & bit)
            return FALSE;
        csp->elements[1] |= bit;
    } else {
        bit = 1 << (tn - 64);
        if (csp->elements[2] & bit)
            return FALSE;
        csp->elements[2] |= bit;
    }
    return TRUE;
}


/*  removes token `t' from set `dsp';
    the result is TRUE iff the set is changed.  */
BOOL remove_element( dsp, tn )
TOKEN_SET *dsp;  int tn;
{
    register SETPTR csp;
    register int bit;

    if (dsp->setsize < tn) return FALSE;
    csp = dsp->setp;
    while( tn >= 3*32 ) {
        tn -= 3*32;
        csp = csp->next;
    }
    if (tn < 32) {
        bit = 1 << tn;
        if ((csp->elements[0] & bit) == 0)
            return FALSE;
        csp->elements[0] ^= bit;
    } else
    if (tn < 64) {
        bit = 1 << (tn - 32);
        if ((csp->elements[1] & bit) == 0)
            return FALSE;
        csp->elements[1] ^= bit;
    } else {
        bit = 1 << (tn - 64);
        if ((csp->elements[2] & bit) == 0)
            return FALSE;
        csp->elements[2] ^= bit;
    }
    return TRUE;
}
/* adds members of set `ss' into set `*dsp';
   the result is TRUE iff the destination set changes */
BOOL test_merge_sets( dsp, ss )
TOKEN_SET *dsp, ss;
{
    register SETPTR dssp, sssp;
    register int pe;
    BOOL changed = FALSE;

    expand_set( dsp, ss.setsize );
    dssp = dsp->setp;
    sssp = ss.setp;
    while( sssp != NULL ) {
        pe = dssp->elements[0];
        if ( pe != (dssp->elements[0] |= sssp->elements[0]) )
            changed = TRUE;
        pe = dssp->elements[1];
        if ( pe != (dssp->elements[1] |= sssp->elements[1]) )
            changed = TRUE;
        pe = dssp->elements[2];
        if ( pe != (dssp->elements[2] |= sssp->elements[2]) )
            changed = TRUE;
        dssp = dssp->next;
        sssp = sssp->next;
    }
    return changed;
}


/* adds members of set `ss' into set `*dsp'; like `test_merge_sets'
   except there is no indication as whether destination changed. */
void merge_sets( dsp, ss )
TOKEN_SET *dsp, ss;
{
    register SETPTR dssp, sssp;

    expand_set( dsp, ss.setsize );
    dssp = dsp->setp;
    sssp = ss.setp;
    while( sssp != NULL ) {
        dssp->elements[0] |= sssp->elements[0];
        dssp->elements[1] |= sssp->elements[1];
        dssp->elements[2] |= sssp->elements[2];
        dssp = dssp->next;
        sssp = sssp->next;
    }
}


/*  tests if token `t' is a member of set `s' */
BOOL member_test( s, tn )
TOKEN_SET s;  register int tn;
{
    register SETPTR csp;

    if (tn > s.setsize) return FALSE;
    for( csp = s.setp;  csp != NULL; csp = csp->next ) {
        if ( tn >= 3*32 ) {
            tn -= 3*32;
            continue;
        }
        if (tn < 32)
            return  (csp->elements[0] & (1 << tn)) != 0 ;
        if (tn < 64)
            return  (csp->elements[1] & (1 << (tn-32))) != 0 ;
        return  (csp->elements[2] & (1 << (tn-64))) != 0 ;
    }
    internal_error( "member_test" );
    exit(-1);
    /*NOTREACHED*/
}


/*  determines number of elements in set `s' */
int cardinality( s )
TOKEN_SET s;
{
    register SETPTR csp;
    register int elems, count;

    count = 0;
    for( csp = s.setp;  csp != NULL;  csp = csp->next ) {
        elems = csp->elements[0];
        while( elems != 0 ) {
            count++;
            elems &=  ( ~( -elems ) );
        }
        elems = csp->elements[1];
        while( elems != 0 ) {
            count++;
            elems &=  ( ~( -elems ) );
        }
        elems = csp->elements[2];
        while( elems != 0 ) {
            count++;
            elems &=  ( ~( -elems ) );
        }
    }
    return count;
}


/*  returns TRUE iff (s1 * s2 * s3) is null  */
BOOL disjoint( s1, s2, s3 )
TOKEN_SET s1, s2, s3;
{
    register SETPTR ssp1, ssp2, ssp3;

    ssp1 = s1.setp;
    ssp2 = s2.setp;
    ssp3 = s3.setp;
    while( ssp1 != NULL && ssp2 != NULL && ssp3 != NULL ) {
        if ( (ssp1->elements[0] & ssp2->elements[0] & ssp3->elements[0])
                != 0 )
            return FALSE;
        if ( (ssp1->elements[1] & ssp2->elements[1] & ssp3->elements[1])
                != 0 )
            return FALSE;
        if ( (ssp1->elements[2] & ssp2->elements[2] & ssp3->elements[2])
                != 0 )
            return FALSE;
        ssp1 = ssp1->next;
        ssp2 = ssp2->next;
        ssp3 = ssp3->next;
    }
    return TRUE;
}
