#  Makefile for ilalr

#  ilalr was created by:
#
#       R. Nigel Horspool
#       Dept. of Computer Science, University of Victoria
#       P.O. Box 1700, Victoria, B.C., Canada  V8W 2Y2
#
#       nigelh@uvunix.bitnet
#       nigelh%csr.uvic.cdn@ubc.csnet

#  If you intend the install the program and its man entry,
#  the definitions for DEST and MAN will need to be changed.

## The full pathnames for the final products
DEST =  /home/nigelh/bin/ilalr
MAN  =  /home/nigelh/lib/ilalr.1

CFLAGS = -g

## Uncomment the next definition to check all malloc & free calls
## (available on SUN system only)
#MALLOC = /usr/lib/debug/malloc.o

##  All the object files that need to be linked to create `ilalr'
OBJS =  main.o addrule.o deleterule.o rules.o starters.o lalr.o \
	lookahead.o conflicts.o readinput.o tokensets.o \
	reachability.o storage.o globals.o print.o work.o \
	commands.o tables.o $(MALLOC)

##  The corresponding source code files
LINTS = main.c addrule.c deleterule.c rules.c starters.c lalr.c \
	lookahead.c conflicts.c readinput.c tokensets.c \
	reachability.c storage.c globals.c print.c work.c \
	commands.c tables.c

##  The complete list of C source code files
SRCS =  $(LINTS) globals.h rules.h tokensets.h lalr.h work.h commands.h

##  The files that ought to be regularly backed up
PRES =  $(SRCS) Makefile

##  The preferred command to list several files
LPR = enscript -2r

.SUFFIXES: .tex .dvi .imp .doc

.tex.dvi:
	latex $*

.dvi.doc:
	dviimp $<
	ipr -Pip $*.imp

.tex.doc:
	latex $*
	dviimp $*.dvi
	ipr -Pip $*.imp

ilalr:  $(OBJS)
	gcc $(CFLAGS) -o ilalr $(OBJS)

doc:    ilalr.doc
	@lpq -Pip

install: ilalr
	install -c -s ilalr $(DEST)
	nroff -man ilalr.man > $(MAN)

help:
	@sed -e 's/^#@  //p' -n Makefile
#@      Makefile targets are:
#@	      ilalr   - the program
#@	      doc     - print the descriptive paper
#@	      install - copy into bin directory
#@	      lint    - perform lint check
#@	      rmbak   - remove editor back-up files
#@	      listing - print changed source files
#@	      clean   - remove .o files, etc.
#@	      safe    - set protection modes on files
#@	      shar    - create a bundled archive

lint:
	lint $(LINTS)

rmbak:
	rm -f *% *.out core *.imp *.dvi *.log

clean:  rmbak
	rm -f *.o *.aux

fulllisting:
	$(LPR) $(SRCS)
	@ date > listing

listing: $(SRCS)
	$(LPR) $?
	@ date > listing

safe:
	-chmod 444 $(PRES)

unsafe:
	-chmod 644 $(PRES)

shar:
	bundle Makefile $(SRCS) ilalr.tex ilalr.1 > shar


##########################################################
#		       DEPENDENCIES		     #
##########################################################

rules.o main.o:	 globals.h rules.h

deleterule.o:	   globals.h rules.h tokensets.h work.h

globals.o:	      globals.h rules.h

addrule.o work.o:       globals.h rules.h lalr.h work.h

readinput.o:    globals.h rules.h tokensets.h storage.h commands.h

starters.o:     globals.h rules.h tokensets.h

print.o:	globals.h rules.h lalr.h tokensets.h

tokensets.o:    globals.h rules.h tokensets.h

lalr.o:	 globals.h rules.h tokensets.h lalr.h work.h storage.h

lookahead.o:    globals.h rules.h tokensets.h lalr.h work.h

conflicts.o:    globals.h rules.h tokensets.h lalr.h work.h

reachability.o: globals.h rules.h lalr.h work.h storage.h

storage.o:      globals.h rules.h lalr.h storage.h tokensets.h

commands.o:     globals.h commands.h

tables.o:       globals.h rules.h tokensets.h storage.h
