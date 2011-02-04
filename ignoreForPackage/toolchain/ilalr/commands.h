/*  commands.h  */

typedef enum {  CMD_NULL, CMD_HELP, CMD_TOKEN, CMD_START,
                CMD_DELETE, CMD_TRACE, CMD_PRINT, CMD_WRITE,
                CMD_COMMENT, CMD_SAVE, CMD_READ, CMD_INCLUDE,
                CMD_CHECK, CMD_CLEAR,
                CMD_QUIT
        } CMDS;

typedef struct {
        char *name;  CMDS cmd;  char *synopsis;  int len;
    } CMDMAP;


extern void print_help();
extern CMDS command_lookup();
extern int match();
