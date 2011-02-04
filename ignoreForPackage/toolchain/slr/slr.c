/*	SLR(1) Parser Generator
	=======================

    Copyright (c)  Gordon V. Cormack  and   R. Nigel Horspool  1985.

    Date of last update:  2 May 1986.

    USAGE:
		slr  [-c]  [-l]  [-d]  [-w width]  [-t]  [gram]

    OPTIONS:

	-c :	don't reduce number of SLR states by combining shift
		actions with reduce actions.

	-l :	generate listing of tokens, grammar and recognizer
		states on the standard output.

	-d :	generate listing of `first', `last' and `follow' sets
		as computed for the grammar.

	-w :	changes the assumed width of the standard output
		device from 72 (the default) to the immediately
		following integer.

	-t :	disables output of machine-readable parsing tables.

	gram :	the name of the file containing the grammar.  If this
		argument is absent, the grammar is read from the
		standard input.

    RESULT:

	If the grammar is free of errors and if the `-t' flag is not
	given, slr parsing tables are generated in a file named
	`gram.tbl', where `gram' is the name of the input file holding
	the grammar.  If the grammar was read from the standard input,
	the tables are written to a file named: `slr.tbl'.

	If the grammar contains errors, diagnostic information is given.
	Unless the '-l' option forces output of all recognizer states,
	just the inadequate states are printed.
*/

#include <stdio.h>
#include <strings.h>
#include <stdlib.h>
#include <ctype.h>

/*char *calloc();*/

#define FALSE	0
#define TRUE	1
#define TERM	0
#define NONTERM	1
#define KHASHSIZE 128	/* must be power of 2 */

typedef struct state_list_item {
		struct kerndesc *rstatep;
		struct state_list_item *next_state;
	    } *STATEP;

typedef int BITVEC[];

typedef struct syrecord {	/* Description of grammar symbol */
		struct syrecord *next_sym;
		short	sym_no;		/* symbol number */
		char	tnt;		/* terminal or non-terminal */
		char	nullable;
		struct ruledesc *firstalt; /* ptr to first alternate */
		BITVEC	*first,
			*last,
			*follow;
		char	symtext[1];	/* text of symbol */
	    }  *SYMPTR; 

typedef struct ruledesc {	/* Description of a production rule */
		struct ruledesc *next_rule;
		short	rule_no,	/* production number */
			nrhs;		/* number of symbols on RHS */
		STATEP	reduce_states;
		SYMPTR	lhstoken;	/* symbol on LHS */
		SYMPTR	rhs[1];		/* symbols on right-hand side */
	      } *RULEPTR;

typedef struct {
		RULEPTR rulep;	/* identity of marked rule */
		short	pos;	/* marked position within RHS */
	    } ITEM;

typedef struct {
		int	kernelhash;
		short	num_items;
		ITEM	item[1];	/* usually has more elements */
	    } ITEMSET;

typedef struct trans {
		struct trans *next_trans;
		SYMPTR	symp;
		union {
		    struct kerndesc *statep;
		    RULEPTR rulep;
		}	rs;
		char	action;	/* S=shift, R=reduce, *=shift-reduce */
		char	flag;	/* helps manage print-outs */
	    } *TRANSP;

typedef struct kerndesc {
		ITEMSET	*itemp;
		struct kerndesc *next_kern, *father_kern, *nxt_in_bkt;
		short	state_no;
		TRANSP	first_trans;
	    } *KERNELPTR;

KERNELPTR docompare();

RULEPTR  first_rule, last_rule;
KERNELPTR kernel_hash[KHASHSIZE];
KERNELPTR first_kernel, last_kernel, fromstate;
ITEMSET *newkernp, *closurep;
int	lastkern = 0;
int	num_rules = 0;
SYMPTR	*worklist;
int	bitvecsize;		/* number of elements in a BITVEC */

SYMPTR	first_sym = NULL, last_sym = NULL;
int	lastsym = 0;
int	c = ' ';		/* current scanned character */

char	*filename;		/* name of grammar input file */
FILE	*infile = stdin;	/* the input file itself */
int	maxcol = 72;		/* width of standard output device */

short	conflict = FALSE;
short	listing = FALSE;
short	dump = FALSE;
short	tables = TRUE;
short	combine_sr_flag = TRUE;

/* Define looping constructs for the main lists in the program */
#define forall_kernels(k) for(k=first_kernel;k!=NULL;k=k->next_kern)
#define forall_rules(r)   for(r=first_rule;r!=NULL;r=r->next_rule)
#define forall_symbols(s) for(s=first_sym;s!=NULL;s=s->next_sym)
#define forall_trans(t,k) for(t=k->first_trans;t!=NULL;t=t->next_trans)
#define forall_reduces(s,r)   for(s=r->reduce_states;s!=NULL;\
					s=s->next_state)
/* Package of bit vector routines */
void vector_or( x, y )
register BITVEC *x, *y;
{
    register int i;
    for( i=0; i < bitvecsize; i++ )
	(*x)[i] |= (*y)[i];
}

#define bit_test(x,pos) ( (*(x))[pos >> 5] & (1 << (pos & 31)) )

void bit_set( x, pos )
BITVEC *x; register int pos;
{
    (*x)[pos >> 5] |= (1 << (pos & 31));
}


BITVEC *new_vector() {
    register BITVEC *vp;

    vp = (BITVEC *)calloc( (unsigned)bitvecsize, sizeof(int) );
    return( vp );
}


/* look up symbol s and return pointer to symbol table entry */
SYMPTR look( s )
char *s;
{
    register SYMPTR sp;

    forall_symbols( sp ) {
	if (sp->symtext[0] != s[0]) continue;
	if (strcmp(sp->symtext, s) != 0) continue;
	return( sp );
    }
    sp = (SYMPTR)calloc( 1, (unsigned)( sizeof(*sp) + strlen(s) ) );
    sp->next_sym = NULL;
    sp->tnt = TERM;
    sp->nullable = 'F';	/* terminals are not nullable */
    strcpy(sp->symtext,s);
    sp->sym_no = lastsym++;
    sp->first = sp->last = sp->follow = NULL;
    if (first_sym == NULL)
	first_sym = sp;
    else
	last_sym->next_sym = sp;
    last_sym = sp;
    return( sp );
}


/* Returns next token in input file.  A token is:
	grammar-symbol or '|' or  '\n'			*/
char *scan() {
    static char tempstring[128];
    register char *s;

    while( isspace(c) ) {
	if (c == '\n') {
	    c = getc(infile);
	    return( "\n" );
	}
	c = getc(infile);
    }
    if (c == EOF) {
	fclose(infile);
	return( "\n" );
    }
    s = tempstring;
    do {
	*s++ = c;
	c = getc(infile);
    } while(c != EOF && !isspace( c ) );
    *s = '\0';
    return( tempstring );
}


void readgram() {
    register RULEPTR rp;
    register SYMPTR lhsp;
    register int  lastrhs;
    register char *s;
    SYMPTR	temprhs[128];
    short	first_alternate;

    while( c != EOF ) {
	s = scan();
	if (*s == '\n') continue;
	if (*s != '%') break;
	if (strcmp(s,"%token") == 0) {
	    for( ; ; ) {
		s = scan();
		if (*s == '\n') break;
		lhsp = look( s );
		if (lhsp != last_sym) {
		    fprintf(stderr,"terminal %s declared twice\n", s );
		}
	    }
	} else {
	    fprintf(stderr,"Unknown directive - %s\n", s);
	    while( *s != '\n' )
		s = scan();
	}
    }
    if (c == EOF) return;
    for( ;  c != EOF;  s = scan() ) {
	if (*s == '\n') continue;
	if (s[0] == '|' && s[1] == '\0')	/* an alternative */
	    first_alternate = FALSE;
	else {				/* a new left-hand side */
	    lhsp = look(s);
	    if (lhsp->tnt == NONTERM)
		fprintf(stderr, "non-terminal %s defined twice\n", s );
	    lhsp->tnt = NONTERM;
	    lhsp->nullable = '?';	/* non-terminals may be null */
	    first_alternate = TRUE;
	}
	for( lastrhs=0; ; ) {
		s = scan();
		if (*s == '\n') break;
		temprhs[lastrhs++] = look(s);
	}
	rp = (RULEPTR)calloc( 1, (unsigned)( sizeof(*rp)
				+ lastrhs*sizeof(rp->rhs[0]) ) );
	rp->rule_no = num_rules++;
	rp->lhstoken = lhsp;
	rp->nrhs = lastrhs;
	while( lastrhs-- > 0 )
		rp->rhs[lastrhs] = temprhs[lastrhs];
	rp->reduce_states = NULL;
	rp->next_rule = NULL;
	if (last_rule == NULL)
	    first_rule = rp;
	else
	    last_rule->next_rule = rp;
	last_rule = rp;
	if (first_alternate) lhsp->firstalt = rp;
    }
}


short col = 0;

/*VARARGS2*/
void cprintf( indent, format, item1, item2, item3 )
char *format;  int indent, item1, item2, item3;
{
    char pbuffer[128];
    register int  len;

    sprintf(pbuffer, format, item1, item2, item3);
    len = strlen(pbuffer);
    if ( (col += len) >= maxcol ) {
	putchar('\n');  col = len;
	while( *format == ' ' ) {
	    format++;  indent++;
	}
	while( indent >= 8 ) {
	    indent -= 8;  col += 8;  putchar( '\t' );
	}
	while( indent-- > 0) {
	    putchar( ' ' );  col++;
	}
    }
    fputs( pbuffer, stdout );
}


void writegram() {
    register RULEPTR rp;
    register SYMPTR sp;
    register int j;

    puts( "Terminal Symbols:" );  col = 999;
    forall_symbols( sp )
	if (sp->tnt == TERM)
	    cprintf( 5, "   %d: %s", sp->sym_no, sp->symtext );
    puts( "\n\nNon-Terminal Symbols:" );  col = 999;
    forall_symbols( sp )
	if (sp->tnt == NONTERM)
	    cprintf( 5, "   %d: %s", sp->sym_no, sp->symtext );

    puts( "\n\nProduction Rules:" );
    forall_rules( rp ) {
	col = 999;
	cprintf( 8, "%3d.\t%s :=", rp->rule_no, rp->lhstoken->symtext );
	for( j=0; j < rp->nrhs; j++ ) {
	    cprintf( 23, " %s", rp->rhs[j]->symtext );
	}
    }
}
 

void emptyset( x )
ITEMSET *x;
{
    x->num_items = 0;
    x->kernelhash = 0;
}


void assign_itemset( dest, source )
register ITEMSET *dest, *source;
{
    register int i;

    dest->kernelhash = source->kernelhash;
    dest->num_items  = source->num_items;
    for( i=0; i < source->num_items; i++ )
	dest->item[i] = source->item[i];
}


void additem( x, r, p )
register ITEMSET *x;  RULEPTR r;  int p;
{
    register ITEM *ip, *jp;
    register int rn;

    rn = r->rule_no;
    ip = x->item;  jp = ip + x->num_items;
    for( ; ip != jp;  ip++ ) {
	if (ip->rulep->rule_no > rn) continue;
	if (ip->rulep->rule_no < rn) break;
	if (ip->pos > p) continue;
	if (ip->pos < p) break;
	return;
    }
    x->num_items++;
    x->kernelhash ^= ((int)r << 4) + p;
    for( ; jp != ip; jp-- )
	*jp = *(jp-1);
    ip->rulep = r;  ip->pos = p;
}


void doclosure(x)
ITEMSET *x;
{
    register int i, k, listend;
    register RULEPTR rp;
    register SYMPTR sp, *workptr;

    workptr = worklist;  listend = 0;
    for( i=0;  i < x->num_items;  i++ ) {
	rp = x->item[i].rulep;
	if ( rp->nrhs > x->item[i].pos ) {
	    sp =  rp->rhs[ x->item[i].pos ];
	    if ( sp->tnt == NONTERM ) {
		workptr[listend] = sp;
		for ( k=0; workptr[k] != sp; k++ )
		    ;
		if ( k == listend)
		    listend++;
	    }
	}
    }
    assign_itemset( closurep, x );
    for( i=0; i<listend; i++ ) {
	for( rp = workptr[i]->firstalt;  rp != NULL &&
		rp->lhstoken == workptr[i]; rp = rp->next_rule ) {
	    additem(closurep,rp,0);
	    if ( rp->nrhs > 0 ) {
		sp = rp->rhs[0];
		if ( sp->tnt == NONTERM ) {
		    workptr[listend] = sp;
		    for( k=0; workptr[k] != sp; k++)
			;
		    if (k == listend)
			listend++;
		}
	    }
	}
    }
}


void doreduce() {
    register int i;
    register RULEPTR rp;
    register STATEP csp;

    for( i=0; i < closurep->num_items; i++ ) {
	rp = closurep->item[i].rulep;
	if ( rp->nrhs == closurep->item[i].pos ) { /* a reduce item */
	    csp = (STATEP)calloc( 1, sizeof(*csp) );
	    csp->rstatep = fromstate;
	    csp->next_state = rp->reduce_states;
	    rp->reduce_states = csp;
	}
    }
}


/*VARARGS4*/
void add_trans( code, kp, sp, nkp )
char code;  SYMPTR sp;  KERNELPTR kp;  char *nkp;
{
    register TRANSP tp, prev_tp, new_tp;
    register int symno, cur_symno;

    prev_tp = NULL;  symno = sp->sym_no;
    forall_trans( tp, kp ) {
	cur_symno = tp->symp->sym_no;
	if (cur_symno >= symno) {
	    if (cur_symno == symno) conflict++;
	    break;
	}
	prev_tp = tp;
    }

    new_tp = (TRANSP)calloc( 1, sizeof(*tp) );
    new_tp->next_trans = tp;
    new_tp->action = code;
    new_tp->symp = sp;
    if (code == 'S')
	new_tp->rs.statep = (KERNELPTR)nkp;
    else
	new_tp->rs.rulep  = (RULEPTR)nkp;
    if (prev_tp == NULL)
	kp->first_trans = new_tp;
    else
	prev_tp->next_trans = new_tp;
}


void donewkern() {
    register int i, j, endlist;
    register RULEPTR rp;
    register SYMPTR sp, *workptr;
    int saved_j;

    workptr = worklist;  endlist = 0;
    for( i=0; i < closurep->num_items; i++ ) {
	rp = closurep->item[i].rulep;
	if ( rp->nrhs > closurep->item[i].pos ) {
	    sp = rp->rhs[closurep->item[i].pos];
	    workptr[endlist] = sp;
	    for( j=0; workptr[j] != sp; j++ )
		;
	    if ( j == endlist )
		endlist++;
	}
    }
    for ( i=0; i < endlist; i++ ) {
	emptyset( newkernp );
	sp = workptr[i];  saved_j = -1;
	for( j=0; j < closurep->num_items; j++ ) {
	    register int rhspos;

	    rp = closurep->item[j].rulep;
	    rhspos = closurep->item[j].pos;
	    if ( rp->nrhs > rhspos  &&  sp == rp->rhs[rhspos] ) {
		if (combine_sr_flag) {
		    if (rp->nrhs == rhspos+1 && saved_j == -1) {
			    /* possible shift-reduce transition */
			saved_j = j;	/* save until we know */
			continue;
		    }
		    if (saved_j >= 0)	/* unsave the item */
			additem(newkernp, closurep->item[saved_j].rulep,
			    closurep->item[saved_j].pos+1);
		    saved_j = -999;		/* prevent item saves */
		}
		additem(newkernp,rp,rhspos+1);
	    }
	}
	if (saved_j >= 0)
	    add_trans( '*', fromstate, sp,
		(char *)(closurep->item[saved_j].rulep) );
	else
	    add_trans( 'S', fromstate, sp,
		(char *)(docompare(fromstate)) );
    }
}


void dostates() {
    emptyset( newkernp );
    additem( newkernp, first_rule, 1 );
    lastkern = 0;
    (void) docompare( (KERNELPTR)NULL );
    forall_kernels( fromstate ) {
	doclosure( fromstate->itemp );
	donewkern();
	doreduce();
    }
}


int compsets( x, y )
register ITEMSET *x, *y;
{
    register int i;

    if (x->kernelhash != y->kernelhash) return( 0 );
    if (x->num_items  != y->num_items)  return( 0 );
    for( i=0; i < x->num_items; i++ )
	if (x->item[i].pos != y->item[i].pos ||
	    x->item[i].rulep != y->item[i].rulep) return( 0 );
    return( 1 );
}


KERNELPTR docompare( fkp )
KERNELPTR fkp;
{
    register KERNELPTR curr_kern;
    register int i;

    i = newkernp->kernelhash & (KHASHSIZE - 1);
    for( curr_kern = kernel_hash[i];
    	    curr_kern != NULL; curr_kern = curr_kern->nxt_in_bkt )
	if (compsets(newkernp, curr_kern->itemp))
	    return( curr_kern );

    curr_kern = (KERNELPTR)calloc( 1, sizeof(*curr_kern) );
    curr_kern->nxt_in_bkt = kernel_hash[i];
    kernel_hash[i] = curr_kern;
    curr_kern->itemp = (ITEMSET *)calloc( 1, (unsigned)( sizeof(ITEMSET)
			+ (newkernp->num_items)*sizeof(ITEM) ) );
    curr_kern->next_kern = NULL;
    assign_itemset( curr_kern->itemp, newkernp );
    curr_kern->state_no = lastkern++;
    curr_kern->first_trans = NULL;
    if (first_kernel == NULL)
	first_kernel = curr_kern;
    else
	last_kernel->next_kern = curr_kern;
    curr_kern->father_kern = fkp;
    last_kernel = curr_kern;
    return( curr_kern );
}


int member( rp, kernp )
RULEPTR rp;  KERNELPTR kernp;
{
    register STATEP csp;
    forall_reduces( csp, rp )
	if (csp->rstatep == kernp) return( 1 );
    return( 0 );
}


void printitem( itp )
ITEM *itp;
{
    register RULEPTR rp;
    register int j;

    rp = itp->rulep;  col = 999;
    cprintf(8, "[[ %d.  %s  ::= ", rp->rule_no, rp->lhstoken->symtext );
    for( j=0; ; j++ ) {
	if (j == itp->pos) cprintf( 16, "  ### " );
	if (j >= rp->nrhs) break;
	cprintf( 15, " %s", rp->rhs[j]->symtext );
    }
    fputs( " ]]", stdout );
}


void printstate( kptr, bad_states_only )
register KERNELPTR kptr;  int  bad_states_only;
{
    register int j;
    short badstate, cnt;
    RULEPTR lastrulep;
    SYMPTR conflict_symp;
    register TRANSP tp;
    TRANSP tp2;

    /* Check to see if this state is inadequate */
    badstate = 0;  conflict_symp = NULL;
    forall_trans( tp, kptr ) {
	if (tp->symp == conflict_symp) {
	    badstate = TRUE;  break;
	}
	conflict_symp = tp->symp;
    }
    if (badstate)
	printf("\n*** The following state contains conflict(s) ***\n");
    else
	if (bad_states_only) return;

    printf( "\nState %d:\n    Kernel Items:", kptr->state_no );
    for( j=0; kptr->itemp->item[j].rulep != NULL; j++ )
	printitem( &( kptr->itemp->item[j] ) );
    cnt = 0;  col = 999;
    forall_trans( tp, kptr ) {
	if ( tp->action == 'S' ) {
	    if (cnt++ == 0)
		printf( "\n    Shift Transitions:" );
	    cprintf(4,"    to state %d on %s",
		tp->rs.statep->state_no, tp->symp->symtext);
	    tp->flag = TRUE;
	} else
	    tp->flag = FALSE;
    }
    cnt = 0;
    forall_trans( tp, kptr ) {
	if ( ! tp->flag && tp->action == 'R' ) {
	    tp->flag = TRUE;  col = 999;
	    if (cnt++ == 0)
		printf( "\n    Reductions:" );
	    lastrulep = tp->rs.rulep;  col = 999;
	    cprintf( 4, "    by rule %d on %s",
		lastrulep->rule_no, tp->symp->symtext );
	    for( tp2=tp; tp2!=NULL; tp2=tp2->next_trans) {
		if (tp2->flag || tp2->action != 'R') continue;
		if (tp2->rs.rulep != lastrulep) continue;
		tp2->flag = TRUE;
		cprintf( 15, " %s", tp2->symp->symtext );
	    }
	}
    }
    cnt = 0;
    forall_trans( tp, kptr ) {
	if ( ! tp->flag && tp->action == '*' ) {
	    tp->flag = TRUE;  col = 999;
	    if (cnt++ == 0)
		printf( "\n    Shift-Reduces:" );
	    lastrulep = tp->rs.rulep;  col = 999;
	    cprintf( 4, "    by rule %d on %s",
		    lastrulep->rule_no, tp->symp->symtext );
	    for( tp2=tp; tp2!=NULL; tp2=tp2->next_trans) {
		if (tp2->flag || tp2->action != '*') continue;
		if (tp2->rs.rulep != lastrulep) continue;
		tp2->flag = TRUE;
		cprintf( 15, " %s", tp2->symp->symtext );
	    }
	}
    }
    putchar( '\n' );
    if (badstate) {
	SYMPTR sentence[50];
	int    slen = 0;
	KERNELPTR fkp, tkp;

	tkp = kptr;
	sentence[slen++] = conflict_symp;
	for( ; ; ) {
	    fkp = tkp->father_kern;
	    if (fkp == NULL) break;
	    forall_trans( tp, fkp )
		if (tp->action == 'S' && tp->rs.statep == tkp) break;
	    if ( slen >= 50 || tp == NULL ) return;
	    sentence[slen++] = tp->symp;
	    tkp = fkp;
	}
	col = 999;
	fputs( "\n    The following sentential form cannot be parsed:",
	    stdout);
	while( --slen >= 0 )
	    cprintf( 6, "  %s", sentence[slen]->symtext );
	puts( "\n    The possibilities for the final symbol are:" );
	forall_trans( tp, kptr )
	    if (tp->symp == conflict_symp) break;
	while( tp!=NULL && tp->symp==conflict_symp ) {
	    if (tp->action != 'R')
		puts( "\tshift" );
	    else
		printf("\treduce by rule %d\n", tp->rs.rulep->rule_no);
	    tp=tp->next_trans;
	}
	putchar( '\n' );
    }
}


void printstates() {
    register KERNELPTR curr_kern;

    if (listing) putchar( '\n' );
    forall_kernels( curr_kern )
	printstate( curr_kern, !listing );
}


void insert_reduces() {
    register KERNELPTR curr_kern;
    register SYMPTR sp;
    register BITVEC *fp;
    register STATEP csp;
    register RULEPTR rp;

    forall_rules( rp ) {
	fp = rp->lhstoken->follow;
	forall_reduces( csp, rp ) {
	    curr_kern = csp->rstatep;
	    forall_symbols( sp ) {
		if (sp->tnt == NONTERM) continue;
		if ( bit_test( fp, sp->sym_no ) )
		    add_trans( 'R', curr_kern, sp, (char *)rp );
	    }
	}
    }
}


void doempty() {
    register int i;
    register SYMPTR sp;
    register RULEPTR rp;
    short done, making_progress;

    do {
	done = TRUE;  making_progress = FALSE;
	forall_symbols( sp ) {
	    if (sp->nullable == '?') {
		short all_non_nullable = TRUE;
		short def_nullable, def_not_nullable;

		done = FALSE;
		for( rp=sp->firstalt; rp != NULL && rp->lhstoken == sp;
			rp = rp->next_rule ) {
		    def_not_nullable = FALSE;
		    def_nullable = TRUE;
		    for( i=0;  i < rp->nrhs;  i++ ) {
			register int x;
			x = rp->rhs[i]->nullable;
			if (x != 'T') def_nullable = FALSE;
			if (x == 'F') {
			    def_not_nullable = TRUE;
			    break;
			}
		    }
		    if (def_nullable) break;
		    if (! def_not_nullable)
			all_non_nullable = FALSE;
		}
		if (def_nullable) {
		    sp->nullable = 'T';
		    making_progress = TRUE;
		} else if (all_non_nullable) {
		    sp->nullable = 'F';
		    making_progress = TRUE;
		}
	    }
	}
    } while( !done && making_progress );

    if (!done) {
	fprintf(stderr,"*** Error, cannot deduce nullability for these \
symbols:-\n\t");
	forall_symbols( sp )
	    if (sp->nullable == '?')
		fprintf(stderr,"  %s", sp->symtext);
	exit(-1);
    }
}


void dofirst() {
    register int i;
    register RULEPTR rp;
    register SYMPTR sp, tp;
    register BITVEC *vp;

    forall_symbols( sp ) {
	sp->first = new_vector();
	bit_set( sp->first, sp->sym_no );
    }
    forall_rules( rp ) {
	vp = rp->lhstoken->first;
	for( i=0;  i < rp->nrhs;  i++ ) {
	    sp = rp->rhs[i];
	    bit_set( vp, sp->sym_no );
	    if ( sp->nullable == 'F' ) break;
	}
    }

    /* Warshall's Algorithm */
    forall_symbols( sp ) {
	i = sp->sym_no;
	forall_symbols( tp ) {
	    if ( bit_test( tp->first, i ) )
		vector_or( tp->first, sp->first );
	}
    }
}


void dolast() {
    register int i, j;
    register RULEPTR rp;
    register SYMPTR sp, tp;
    register BITVEC *vp;

    forall_symbols( sp ) {
	sp->last = new_vector();
	bit_set( sp->last, sp->sym_no );
    }
    forall_rules( rp ) {
	vp = rp->lhstoken->last;
	for( j=rp->nrhs-1;  j >= 0;  j-- ) {
	    sp = rp->rhs[j];
	    bit_set( vp, sp->sym_no );
	    if ( sp->nullable == 'F' ) break;
	}
    }

    /* Warshall's Algorithm */
    forall_symbols( sp ) {
	i = sp->sym_no;
	forall_symbols( tp ) {
	    if ( bit_test( tp->last, i ) )
		vector_or( tp->last, sp->last );
	}
    }
}


void dofollow() {
    register int j, jj;
    register RULEPTR rp;
    register SYMPTR sp, tp, up;

    forall_symbols( sp ) {
	sp->follow = new_vector();
    }

    forall_rules( rp ) {
	for( j = rp->nrhs - 2; j >= 0; j-- ) {
	    sp = rp->rhs[j];
	    for( jj=j+1; jj < rp->nrhs; jj++ ) {
		tp = rp->rhs[jj];
		forall_symbols( up ) {
		    if ( bit_test( sp->last, up->sym_no ) )
			vector_or( up->follow, tp->first );
		}
		if ( tp->nullable == 'F' ) break;
	    }
	}
    }
}


void dumpsets() {
    register SYMPTR sp, tp;

    puts( "\tList of First, Last and Follow sets:" );
    forall_symbols( sp ) {
	col = 999;
	cprintf(4, "Symbol %s    (%s)", sp->symtext,
	    sp->nullable=='T' ? "nullable" : "non-nullable" );
	col = 999;
	fputs( "\n\tFirst:", stdout );
	forall_symbols( tp ) {
	    if ( bit_test( sp->first, tp->sym_no ) )
		cprintf( 14, "  %s", tp->symtext );
	}
	col = 999;
	fputs( "\n\tLast:", stdout );
	forall_symbols( tp ) {
	    if ( bit_test( sp->last, tp->sym_no ) )
		cprintf( 14, "  %s", tp->symtext );
	}
	col = 999;
	fputs( "\n\tFollow:", stdout );
	forall_symbols( tp ) {
	    if ( bit_test( sp->follow, tp->sym_no ) )
		cprintf( 14, "  %s", tp->symtext );
	}
	putchar( '\n' );
    }
}


void writetbl() {
    register KERNELPTR curr_kern;
    register int i, j;
    register RULEPTR rp;
    SYMPTR sp;
    TRANSP tp;
    char tblfilename[128];
    FILE *tbl;

    if (filename != NULL) {
	strcpy( tblfilename, filename );
	strcat( tblfilename, ".tbl" );
    } else
	strcpy( tblfilename, "slr.tbl" );

    tbl = fopen( tblfilename, "w");
    if (tbl == NULL) {
	fprintf(stderr, "cannot create %s\n", tblfilename);  exit(-1);
    }
    fprintf(tbl, "%d %d %d\n", lastsym, num_rules, lastkern );
    forall_symbols( sp )
	fprintf(tbl, "%d %s\n", (int)(sp->tnt), sp->symtext );
    forall_rules( rp ) {
	fprintf(tbl, "%d %d", rp->lhstoken->sym_no, rp->nrhs );
	for( j=0; j<rp->nrhs; j++ )
	    fprintf(tbl, " %d", rp->rhs[j]->sym_no );
	fprintf(tbl, "\n");
    }
    forall_kernels( curr_kern ) {
	i = 0;
	forall_trans( tp, curr_kern )
		i++;
	fprintf(tbl, "%d", i );
	forall_trans( tp, curr_kern ) {
	    fprintf(tbl, " %d %c%d", tp->symp->sym_no, tp->action,
		(tp->action == 'S')? tp->rs.statep->state_no :
		tp->rs.rulep->rule_no );
	}
	putc( '\n', tbl );
    }
    fclose( tbl );
}


void alloc_stg() {
    register int maxsize, maxitems = 1;
    register RULEPTR rp;

    forall_rules( rp )
	maxitems += rp->nrhs + 1;
    maxsize = sizeof(ITEMSET) + maxitems*sizeof(ITEM);
    newkernp = (ITEMSET *)calloc( 1, (unsigned)maxsize );
    closurep = (ITEMSET *)calloc( 1, (unsigned)maxsize );
    bitvecsize = (lastsym + 31) >> 5;
    worklist = (SYMPTR *)calloc( (unsigned)lastsym, sizeof(SYMPTR) );
}


void main( argc, argv )
int argc;  char **argv;
{
    int i;
    char *cp;

    for( i=1; i<argc; i++ ) {
	cp = argv[i];
	if (*cp == '-') {	/* an option */
	    cp++;
	    if (*cp == 'c') {
		combine_sr_flag = FALSE;
		continue;
	    } if (*cp == 'd') {
		dump = TRUE;
		continue;
	    }
	    if (*cp == 'l') {
		listing = TRUE;
		continue;
	    }
	    if (*cp == 'w') {
		maxcol = atoi(cp+1);
		if (maxcol < 10) maxcol = 72;
		continue;
	    }
	    if (*cp == 't') {
		tables = FALSE;
		continue;
	    }
	    fprintf(stderr, "unknown option (-%s)\n", cp);
	    continue;
	}
	if (filename != NULL) {
	    fprintf(stderr, "only one file argument permitted\n");
	    continue;
	}
	filename = cp;
    }

    if (filename != NULL) {
	infile = fopen( filename, "r" );
	if (infile == NULL) {
	    fprintf(stderr,"cannot read %s\n", filename);
	    exit(-1);
	}
    }

    readgram();
    alloc_stg();
    doempty();
    dofirst();
    dolast();
    dofollow();
    if (listing) writegram();
    if (dump) dumpsets();
    dostates();
    insert_reduces();
    if (listing || conflict) printstates();
    if (!conflict && tables) writetbl();
    exit( conflict );
}

show_symbols()
{
    SYMPTR p;

    for (p = first_sym; p; p = p->next_sym) {
	printf("symbol <%s>\n", p->symtext);
    }
}    
