/* kano-get-start-time.c
 *
 * Copyright (C) 2015 Kano Computing Ltd.
 * License: http://opensource.org/licenses/MIT
 * 
 * This file implements a command to get the start time of a process
 * kano-get-start-time <pid>
 */



#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

#include "get-start-time.h"

void usage(void){
   fprintf(stderr,"Usage: kano-get-start-time <pid>\n");
   exit(1);
}

int main(int argc,char *argv[]){
  pid_t pid;
  if(argc!=2){
    usage();
  }
  int ret=sscanf(argv[1],"%d",&pid);
  if(ret!=1){
    usage();
  }
  unsigned long long st=get_process_start_time(pid);
  printf("%lld\n",st);
  return 0;
}  
