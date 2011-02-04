/*  readinput.c  */

#include <ctype.h>
#include <strings.h>
#include "globals.h"
#include "rules.h"
#include "tokensets.h"
#include "storage.h"
#include "commands.h"


#define MAXTOKENNUM     255     /* max allowed terminal token number */
#define MAXLEN          512     /* max length of input line */
#define MAXRHSLEN       20      /* max no of symbols on RHS */
#define MAXDEPTH        10      /* max nesting of include files */

#define SKIPFN(x,fn)    while( *(x) != '\0' && fn(*(x)) ) ((x)++)

static char *DEFAULT_TABLE_FILE = "lalr.tbl";
static char *DEFAULT_GRAM_FILE = "gram";
static FILE *filestack[MAXDEPTH];
static BOOL cur_is_tty;
static int fdepth = 0;
static char lastlhstext[MAXLEN];        /* current LHS */
static BOOL changed_gram = FALSE;
static int nextdelim = 0;




void push_file( fn )
char *fn;
{
    FILE *newstream;

    if ((fdepth+1) >= MAXDEPTH) {
        (void)fprintf(stderr, "Too many nested %%include files\n");
        return;
    }
    newstream = fopen( fn, "r" );
    if (newstream == NULL) {
        perror( fn );
        return;
    }
    filestack[fdepth++] = curstream;
    curstream = newstream;
    cur_is_tty = isatty(fileno(curstream));
}


int pop_file() {
    if (--fdepth < 0) return -1;
    curstream = filestack[fdepth];
    cur_is_tty = isatty(fileno(curstream));
    return 0;
}


/*  Create super-rule of form
        S  ::=   X  -|
    where X is the new token and S is a `super-goal'  */
void create_super_rule( t )
TOKEN t;
{
    RULE newrule;
    TOKEN newt;
    char buff[10];

    nextdelim++;
    newrule = obtain_rule( 2 );
    newrule->lhs = supergoal;

    newrule->rhs[0] = t;
    newt = create_token( (sprintf(buff, " -|%03d ", nextdelim),buff) );
    newt->kind = TERMINAL;
    newrule->rhs[1] = newt;
    newrule->rhs[2] = NULLTOKEN;

    insertrule( newrule );
    init_for_new_token( t, newrule );

}


static char *scantoken( cp, tp, create )
char *cp;  TOKEN *tp;  BOOL create;
{
    char tokentext[MAXLEN];
    char *tcp = tokentext;
    register TOKEN tkp;

    if (*cp == '\0' || isspace(*cp))
        internal_error("scantoken");
    do {
        *tcp++ = *cp++;
    } while( *cp != '\0' && !isspace(*cp) );
    *tcp = '\0';
    SKIPFN(cp,isspace);

    foreach_token( tkp ) {
        if (strcmp(tkp->tokenname,tokentext) == 0) {
            *tp = tkp;
            return cp;
        }
    }

    *tp = create? create_token( tokentext ) : NULLTOKEN;

    return cp;
}


static char *extract_file_name( clp )
char *clp;
{
    char *fn;

    SKIPFN(clp,isspace);
    if (*clp == '\0')
        return NULL;
    if (*clp == '"') {
        fn = clp+1;
        do {
            clp++;
        } while( *clp != '\0' && *clp != '\n' && *clp != '"' );
    } else {
        fn = clp;
        do {
            clp++;
        } while( *clp != '\0' && *clp != '\n' );
    }
    *clp = '\0';
    return fn;
}


static BOOL query_user( prompt )
char *prompt;
{
    char response[MAXLEN];
    if (!changed_gram || !cur_is_tty)
        return TRUE;
    for( ; ; ) {
        (void)fprintf(stderr, "%s?  (y/n)  ", prompt );
        (void)fgets(response, sizeof(response), curstream);
        if (response[0] == 'y' || response[0] == 'Y') return TRUE;
        if (response[0] == 'n' || response[0] == 'N') return FALSE;
    }
    /*NOTREACHED*/
}


static void check_for_new_nt( lhs )
register TOKEN lhs;
{
    if (lhs->kind == TERMINAL) {
        (void)fprintf(stderr, "Warning: `%s' was previously declared \
as a terminal symbol\n", lhs->tokenname );
        lhs->kind = NOT_ON_LHS;
        lhs->outputnum = -1;
    }
    if (lhs->kind == NOT_ON_LHS) {
        lhs->kind = NON_NULL_NT;
        create_super_rule( lhs );
    }
}


static int control_line( clp )
char *clp;
{
    TOKEN t, lhs;
    RULE r;
    int k, altnum;
    char *fn;
    static char last_print_cmd[MAXLEN] = "rules";

    clp++;
    SKIPFN(clp, isspace);
    if (*clp == '\0') return 0;
    switch( command_lookup( &clp ) ) {

    case CMD_TOKEN:
        for( ; ; ) {
            SKIPFN(clp,isspace);
            if (*clp == '\0') break;
            clp = scantoken( clp, &t, TRUE );
            if (t->firstdefn != NULLRULE) {
                (void)fprintf(stderr,
                    "Error: `%s' appears on the LHS of a production\n",
                    t->tokenname );
                /* ignore any token number that follows */
                SKIPFN(clp,isspace);
                SKIPFN(clp,isdigit);
                continue;
            }
            t->kind = TERMINAL;
            SKIPFN(clp,isspace);
            if (*clp != '\0' && isdigit(*clp)) {
                k = atoi(clp++);
                SKIPFN( clp, isdigit );
                if (k > 0 && k < MAXTOKENNUM) {
                    set_outputnum( t, k );
                    changed_gram = TRUE;
                    continue;
                }
                (void)fprintf(stderr,
                    "Token numbers must be in range 1 .. %d\n",
                    MAXTOKENNUM );
            }
            set_outputnum( t, 0 );
            changed_gram = TRUE;
        }
        break;

    case CMD_START:
        SKIPFN(clp,isspace);
        if (*clp == '\0') {
            if ( goalsymbol == NULLTOKEN )
                cprintf( "No goal symbol has been defined\n" );
            else
                cprintf( "Current start symbol is `%s'\n",
                        goalsymbol->tokenname );
            break;
        }
        clp = scantoken( clp, &t, TRUE );
        check_for_new_nt( t );
        if (goalsymbol != NULLTOKEN && goalsymbol != t) {
            (void)fprintf(stderr, "Previous goal symbol was `%s'\n",
                goalsymbol->tokenname );
            changed_gram = TRUE;
        }
        goalsymbol = t;
        break;

    case CMD_PRINT:
        SKIPFN(clp,isspace);
        if ( *clp == '\0' ) {
            clp = last_print_cmd;
            cpreset();
            cprintf( "  %%print %s", clp );
        } else
            (void)strcpy( last_print_cmd, clp );

        if (match(clp, "tokens", 1)) {  /* tokens */
            print_tokens();
            break;
        }
        if (match(clp, "rules", 1)) {   /* rules */
            SKIPFN(clp,isalnum);
            SKIPFN(clp,isspace);
            lhs = NULLTOKEN;
            if ( *clp != '\0' )
                (void)scantoken( clp, &lhs, FALSE );
            print_rules( lhs );
            break;
        }
        if (match(clp, "starters", 4)) {        /* starters */
            print_starters();
            break;
        }
        if (match(clp, "null", 1)) {            /* nullables */
            print_nullability();
            break;
        }
        if (match(clp, "states", 4)) {          /* states */
            print_lalr();
            break;
        }
        if (match(clp, "uses", 1)) {            /* uses of a symbol */
            SKIPFN(clp,isalnum);
            SKIPFN(clp,isspace);
            lhs = NULLTOKEN;
            if ( *clp != '\0' )
                (void)scantoken( clp, &lhs, FALSE );
            if (lhs != NULLTOKEN)
                print_uses( lhs );
            else
                (void)fprintf(stderr,"Token not used in grammar\n");
            break;
        }
        (void)fprintf(stderr, "unrecognized print option - %s", clp );
        (void)strcpy( last_print_cmd, "rules" );
        break;

    case CMD_CHECK:
        if (check_rules())
            cprintf( "All symbols and rules are accessible\n" );
        break;

    case CMD_DELETE:
        SKIPFN(clp,isspace);
        if (*clp == '\0') {
            (void)fprintf(stderr,
                "Missing LHS symbol for rule to delete\n");
            break;
        }
        clp = scantoken( clp, &lhs, FALSE );
        if (lhs == NULLTOKEN) {
            (void)fprintf(stderr,"No token with this name exists\n");
            break;
        }
        if (lhs->kind == TERMINAL || lhs->kind == NOT_ON_LHS) {
            (void)fprintf(stderr,"No rules with this LHS exist\n");
            break;
        }
        k = altnum = (*clp == '\0')?  0 : atoi(clp);
        foreach_rule_with_lhs(lhs,r) {
            if (--k <= 0) break;
        }
        if (k > 0) {
            (void)fprintf(stderr,"Alternate #%d does not exist\n",
                altnum);
            break;
        }
        cprintf( "Deleting rule:\n" );
        print_rule( r );
        deleterule( r );
        changed_gram = TRUE;
        break;

    case CMD_INCLUDE:
        fn = extract_file_name( clp );
        if (fn == NULL) {
            fn = DEFAULT_GRAM_FILE;
            fprintf(stderr,"Including grammar from file: %s\n", fn);
        }
        push_file( fn );
        break;

    case CMD_QUIT:
        k = pop_file();
        if (k < 0 && !query_user( "Quit without saving changes" ))
            k = 0;
        return k;

    case CMD_READ:
        fn = extract_file_name( clp );
        if (fn == NULL) {
            fn = DEFAULT_TABLE_FILE;
            fprintf(stderr,"Reading tables from file: %s\n", fn);
        }
        read_tables( fn );
        changed_gram = TRUE;
        break;

    case CMD_WRITE:
        fn = extract_file_name( clp );
        if (fn == NULL) {
            fn = DEFAULT_TABLE_FILE;
            fprintf(stderr,"Writing tables to file: %s\n", fn);
        }
        write_tables( fn );
        changed_gram = FALSE;
        break;

    case CMD_SAVE:
        fn = extract_file_name( clp );
        if (fn == NULL) {
            fn = DEFAULT_GRAM_FILE;
            fprintf(stderr,"Saving grammar in file: %s\n", fn);
        }
        save_state( fn );
        changed_gram = FALSE;
        break;

    case CMD_CLEAR:
        if (query_user( "Throw away all current rules" )) {
            release_all();
            changed_gram = FALSE;
        }
        break;

    case CMD_COMMENT:
        break;

    case CMD_HELP:
        print_help();
        break;
     
    default:
        (void)fprintf(stderr, "Type %%help for a list of commands\n");
        break;

    }
    return 0;
}


/*  Reads input lines up to end of file  */
void readinput() {
    char line[MAXLEN], *savedcp, ch;
    register char *cp;
    TOKEN lhs, rhs[MAXRHSLEN];
    int  rhslen;
    RULE newrule;

    for( ; ; ) {
        if (cur_is_tty) {
            putchar( '>' );  putchar( ' ' );  (void)fflush(stdout);
        }
        cp = fgets( line, sizeof(line), curstream );
        if (cp == NULL) {
            if (pop_file() >= 0) continue;
            break;
        }
        /*  echo included lines -- but not if we are
            running in `batch' mode.                    */
        if (curstream != stdin && outfilename == NULL)
            (void)printf( ">>>\t%s", line );
        if (*cp == '%') {
            if (control_line( cp ) >= 0) continue;
            break;
        }
        SKIPFN( cp, isspace );
        if (*cp == '\0')
            continue;
        if (*cp == '|' && (isspace(cp[1]) || cp[1] == '\0')) {
            if ( lastlhstext[0] == '\0' )
                lhs = NULLTOKEN;
            else
                (void)scantoken( lastlhstext, &lhs, FALSE );
            if (lhs == NULLTOKEN) {
                (void)fprintf(stderr, "Error: no LHS defined\n");
                continue;
            }
            cp++;
            SKIPFN( cp, isspace );
        } else {
            savedcp = cp;
            cp = scantoken( cp, &lhs, TRUE );
            ch = *cp;
            *cp = '\0';
            (void)strcpy( lastlhstext, savedcp );
            *cp = ch;
        }
        check_for_new_nt( lhs );

        for( rhslen=0;  *cp != '\0';  rhslen++ )
            cp = scantoken( cp, &( rhs[rhslen] ), TRUE );
        rhs[rhslen] = NULLTOKEN;

        newrule = obtain_rule( rhslen );
        newrule->lhs = lhs;
        while( rhslen >= 0 ) {
            newrule->rhs[rhslen] = rhs[rhslen];
            rhslen--;
        }

        addrule( newrule );
        changed_gram = TRUE;
    }
}


void init_rules() {
    firsttoken = supergoal = create_token( " \b** \bS \b**" );
    supergoal->kind = NON_NULL_NT;
    goalsymbol = NULLTOKEN;
    cur_is_tty = isatty( fileno(curstream) );
    nextdelim = 0;
}
