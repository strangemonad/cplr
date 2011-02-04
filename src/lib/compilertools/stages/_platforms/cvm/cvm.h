/*
 * This file contains the implementation of the C-VM.
 */

// XXX lot's more comments.

#include <stdio.h>

#include "gc.h"


/*******************************************************************************
 * Arithmetic operations --
 ******************************************************************************/
// XXX TODO, define.



/*******************************************************************************
 * Meta-data operations --
 ******************************************************************************/


/*
 * CVM_VERSION --
 *
 *      Think of this as a CPUID equivalent for the C-VM
 */

// XXX should this be gc_printf?
#define CVM_VERSION printf("You've compiled a C-VM program (version 1.0).\n");
