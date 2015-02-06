/* get-start-time.c
 *
 * Copyright (C) 2015 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
 * 
 * This file exports a function for extracting a process starttime from proc.
 * The idea is to avoid sending signals to a process which has obtained the same pid
 * as the one you intended to send it to.
 */

#include <unistd.h>
#include <stdio.h>

#include "get-start-time.h"

/* extract process start time from /proc/<pid>/stat */
/* If anything goes wrong, return 0 */
unsigned long long get_process_start_time(pid_t pid){
  char filename[255];

  int ret=snprintf(filename,255,"/proc/%d/stat",pid);
  
  /* check for string too long */
  if(ret>=255) return 0; 

  FILE *f=fopen(filename,"r");
  if(!f) return 0;

  /* scan the file, ignoring most of the results */
  unsigned long long starttime;
  ret=fscanf(f, /* pid*/  "%*d "     
	    /* comm    */ "%*s " 
	    /* state   */ "%*c "
            /* ppid    */ "%*d "   
            /* pgrp    */ "%*d "   
            /* session */ "%*d "
	    /* tty_nr  */ "%*d	"
            /* tpgid   */ "%*d "  
	    /* flags   */ "%*u "
            /* minflt  */ "%*lu "
            /* cminflt */ "%*lu "
            /* majflt  */ "%*lu "
            /* cmajflt */ "%*lu "
	    /* utime   */ "%*lu "
	    /* stime   */ "%*lu "
	    /* cutime  */ "%*ld "
            /* cstime  */ "%*ld "
            /* priority*/ "%*ld "
	    /* nice    */ "%*ld " 
            /* num_threads */ "%*ld "
  	    /* itrealvalue */ "%*ld "
	    /* starttime */ "%llu ",&starttime);
  fclose(f);
  if(ret!=1) return 0;
  return starttime;
}

