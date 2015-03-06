// kano-kill-ns
//
// Copyright (C) 2015 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// kills given pids if they are in the given namespace.
// usage: kano-kill-ns <signal> <namespace> pid1 pid2 pid3...
// 
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#define __USE_POSIX
#include <signal.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>

#include "kano-log.h"
#define PATH_LEN 256
#define LINK_LEN 256

int main(int argc,char *argv[]) 
{
  int i;
  if(argc<3){
    kano_log_error("kano-kill-ns: too few arguments\n");
    exit(1);
  }
  // parse first two arguments
  int signum=atoi(argv[1]);
  int count;
  char *end;
  ino_t tokill=strtoull(argv[2],&end,10);
  if(*end!=0) {
    kano_log_error("kano-kill-ns: ns inode not a number\n");
    exit(1);
  }
  int err;

  // now send signal to each pid
  for(i=3;i<argc;i++) {

    char path[PATH_LEN];
    unsigned int pid=strtol(argv[i],&end,10);
    if(*end != 0){
      kano_log_warning("kano-kill-ns: invalid pid %s, skipping\n",argv[i]);
      continue;
    }
    // examine /proc/<pid>/ns/uts to see if it is the same as the inode we have
    // been given
    count=snprintf(path,PATH_LEN,"/proc/%d/ns/uts",pid);
    if(count=0 || count==PATH_LEN){
      kano_log_warning("kano-kill-ns: path too long for %s, skipping\n",argv[i]);
      continue;      
    }
    struct stat statbuf;
    err=stat(path,&statbuf);
    if(err){
       kano_log_warning("kano-kill-ns failed to stat %s\n",path);
       continue;
    }
    // if matched, send the signal
    if(statbuf.st_ino==tokill){
      kano_log_info("kano-kill-ns: killing %d\n",pid);
      int err= kill(pid, signum);      
      if(err) kano_log_warning("kano-kill-ns failed to kill %d\n",pid);
    }
  }
  return 0;
}

