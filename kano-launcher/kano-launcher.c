// kano-launcher
//
// Copyright (C) 2015 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// A simple progeam to launch Kano projects
// Usage: kano-launcher cmd [preset]
//
// reads its configuration from /etc/kano-launcher.conf.d
// 


#define _GNU_SOURCE             /* See feature_test_macros(7) */
#include <sched.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mount.h>
#include <stdio.h>
#include <dirent.h>
#include <string.h>
#include <errno.h>
#include <stdbool.h>
#include <fcntl.h>

#include "kano_c_logging.h"

#define CONF_DIR "/usr/share/kano-toolset/kano-launcher/conf"

#define STRING_SIZE 256
#define PAGE_SIZE  4096
#define STACK_SIZE PAGE_SIZE*4

// uid and gid saved here to allow dropping root privilege
int gid;
int uid;
// The path of the container directory
char contdir[STRING_SIZE];
bool contdir_set=false; // true when we have set contdir

// Configuration file format
// The presence of a configuration file indicates that the app should be containerised.
// The filename is matched to the name of the preset.

typedef struct {
  bool no_kill;           ///< If true, don't kill other apps when launching this one.
                          ///< Default false
  bool match_only_preset; ///< Don't match in the command string
  char extra_cmd[STRING_SIZE];    ///< extra command to run when launching this app
  

}config;


/**
 * @name read_config - Read a config from a particular file
 * @param config_filename - Name of file to read
 * @param matching_cmd - we are matching a string in the command line
 * @param match - Set if we managed to read a file
 * @param conf -  config to write
 * @return int  - zero on success
 */
int read_config(char *config_filename,bool matching_cmd,bool *match,config *conf){
  // default config
  config c={
    .no_kill=false,
    .match_only_preset=false,
    .extra_cmd={0}
  };

  FILE *conf_file=fopen(config_filename,"r");
  char line[STRING_SIZE];
  if(!conf_file) return 1;
    
  while(!feof(conf_file)){
    if(!fgets(line,STRING_SIZE,conf_file)){      
      if(ferror(conf_file)) {
	fclose(conf_file);
	return 1;
      }
      break;
    }	 

    if(strncmp(line,"no_kill",7)==0){
      kano_log_debug("kano-launcher: config %s no_kill\n",config_filename);
      c.no_kill=true;
    }

    if(strncmp(line,"match_only_preset",17)==0){
      kano_log_debug("kano-launcher: config %s match_only\n",config_filename);
      c.match_only_preset=true;
    }

    if(strncmp(line,"extra_cmd:",10)==0){
      kano_log_debug("kano-launcher: config %s extra cmd %s\n",config_filename,&line[10]);
      strncpy(c.extra_cmd,&line[10],STRING_SIZE);
    }
    
  }
  fclose(conf_file);
  if(c.match_only_preset && matching_cmd)
    return 0; // don't write back match
  
  *match=true;
  *conf=c;
  return 0;
}

/**
 * @name is_pi2 - Return true if running on a pi2, false otherwise
 * @return bool
 */
bool is_pi2(void)
{
  FILE *cpu=fopen("/proc/cpuinfo","r");
  char line[STRING_SIZE];
  bool pi2=false;
  unsigned long long rev;
  while(!feof(cpu)){
    if(!fgets(line,STRING_SIZE,cpu)) break;
    if(strncmp("Revision",line,8)==0){
      int count=sscanf(line,"Revision : %llx",&rev);
      if(count==1){
	pi2= (rev & 0xffffff) >= 0x00A01041;
	  break;
      }
    }
  }
  fclose(cpu);
  return pi2;
}


/**
 * @name get_config - find a config file for the current command
 * @param preset - Identifier for the command
 * @param command - command line
 * @param match -  we write to true if we found a file
 * @param conf -  Config to write
 * @return int  - zero on success
 */
int get_config(char *preset, char *command,bool *match,config *conf){
  
  int err=0;
  char conf_filename[STRING_SIZE];
  *match=0;
  if(preset){
    snprintf(conf_filename,STRING_SIZE,"%s/%s",CONF_DIR,preset);
  
    err=read_config(conf_filename,false,match,conf);
    if(!err) return 0;
  }

  // try looking for a filename matching the command
  DIR *conf_dir=opendir(CONF_DIR);
  if(!conf_dir) return 1;

  struct dirent *d;
  
  while((d=readdir(conf_dir))){
    kano_log_debug("kano-launcher: config %s\n",d->d_name);
    if(d->d_type==DT_REG && strstr(command,d->d_name)){
      kano_log_debug("kano-launcher: config %s matched\n",d->d_name);
      snprintf(conf_filename,STRING_SIZE,"%s/%s",CONF_DIR,d->d_name);
      read_config(conf_filename,true,match,conf);
      if(match) break;
    }

  }
  closedir(conf_dir);
    
  return 0;
}

/**
 * @name fatal - We have a fatal error, so log it and quit
 * @param msg - message
 * @return void
 */
void fatal(char *msg){
  perror(msg);
  exit(1);
}

/**
 * @name run_in_container - Function called by clone(2) to start inside a container.
 * @param cmd - Command to run
 * @return int - return value from system(2)
 *
 * This function is run inside the container. It binds the file
 * /proc/<pid>/ns/uts to a file under ~/.kano-app-containers so
 * we can find it later.
 * 
 * Even if we fail to do this, we still try to run the app.
 * Before doing so, we drop root privilege
 */
int run_in_container(void *cmd){
  
  int  err;
  pid_t pid=getpid();
  char piddir[STRING_SIZE];
  int  made_contfile=0;
  char my_contfile[STRING_SIZE];    

  // Choose a name for the contaimer file
  // and make an empty file to bind on top of.
  do {
    int count=snprintf(piddir,STRING_SIZE,"/proc/%d/ns/uts",pid);
    if(count==0 || count==STRING_SIZE) {
      kano_log_error("kano-launcher: string too long \n");
      break;
    }
  
    for(int i=0;i<10;i++){
      int count=snprintf(my_contfile, STRING_SIZE,"%s/%d.%d",contdir,pid,i);
      int cf;
      if(count==0 || count==STRING_SIZE) {
	kano_log_error("kano-launcher: string too long making container file [%s]\n",contdir);
      }
      cf=open(my_contfile,S_IWUSR | S_IRUSR | S_IXUSR);
      if(cf){
	made_contfile=1;
	close(cf);
	break;
      }
    }   

    if(!made_contfile){
      kano_log_error("kano-launcher: failed to make container file for [%s]\n",cmd);
      break;
    }
  }while(0);

  // Now bind the UTS namespace file on top of our empty file
  kano_log_debug("kano-launcher: binding [%s] in to %s \n",piddir,my_contfile);
  err = mount(piddir,my_contfile,NULL, MS_BIND, NULL);
  if(err){
    kano_log_error("kano-launcher: failed to bind mount container for [%s]\n",cmd);
  }

  /* process is running as root, drop privileges */
  if (setgid(gid) != 0)
    fatal("setgid: Unable to drop group privileges");
  if (setuid(uid) != 0)
    fatal("setuid: Unable to drop user privileges:");

  // Run the actual command
  kano_log_info("kano-launcher: starting [%s]\n",cmd);
  err=system(cmd);
  if(err==-1){
    kano_log_error("kano-launcher: unable to start [%s] in container\n",cmd);
  }
  return err;
}
/**
 * @name run_system - drop root priviledge and run a command 
 * @param cmd - Command to run
 * @return int  - return value from system(2)
 */
int run_system(void *cmd){
  // this function is used when we need to run a command which should not be containerised,
  // but  we still need to drop suid root.
  int err;
  /* process is running as root, drop privileges */
  if (setgid(gid) != 0)
    fatal("setgid: Unable to drop group privileges");
  if (setuid(uid) != 0)
    fatal("setuid: Unable to drop user privileges:");

  kano_log_info("kano-launcher: starting [%s]\n",cmd);
  err=system(cmd);
  if(err==-1){
    kano_log_error("kano-launcher: unable to start [%s]\n",cmd);
  }    
  return err;
}

/**
 * @name run_container - run a command
 * @param in_container - if true, run in a container
 * @param cmd - command to run
 * @return int - return value from clone
 */
int run_container(bool in_container,char *cmd){
  // Run a command, either in a container or not.
  int flags=CLONE_PARENT;
  int (*fn)(void *);
  
  if(in_container && contdir_set){
    flags |= CLONE_NEWUTS;
    
    fn=run_in_container;
  }else{
    fn=run_system;
  }
  
  char * stack = (char *)mmap(NULL, STACK_SIZE , \
		      PROT_READ | PROT_WRITE, MAP_PRIVATE | \
		      MAP_ANON | MAP_GROWSDOWN, -1, 0);

  if(stack==MAP_FAILED) fatal("unable to obtain stack\n");

  pid_t cpid;
  long ret=clone(fn,(void *)(stack+STACK_SIZE),flags,cmd,NULL,NULL,NULL);
  return ret;
}

int kill_container(char *cont){
  char my_contfile[STRING_SIZE];
  char my_uts[STRING_SIZE];
  char path[STRING_SIZE];
  char kill_cmd[STRING_SIZE];
  int count;
  int err;
  do {
    char *user_name=getenv("USER");
    if(!user_name) {
      kano_log_error("kano_launcher: $USER not set\n");
      break;
    }
      
    snprintf(my_contfile, STRING_SIZE,"%s/%s",contdir,cont);
    if(count==0 || count==STRING_SIZE) {
      kano_log_error("kano-launcher: error composing contdir string: too long\n");
      break;
    }

    do {
      snprintf(my_uts, STRING_SIZE,"%s/%s",contdir,cont);
      if(count==0 || count==STRING_SIZE) {
	kano_log_error("kano-launcher: error composing uts string: too long\n");
	break;
      }

      struct stat statbuf;
      err=stat(my_uts,&statbuf);
      if(err) {
	kano_log_error("kano-launcher: failed to read inode %s\n",my_uts);
	break;
      }

      count=snprintf(kill_cmd, STRING_SIZE, "pgrep -u %s | xargs kano-kill-ns 15 %lld ", user_name, statbuf.st_ino);
      if(count==0 || count==STRING_SIZE) {
	kano_log_error("kano-launcher: error composing kill command string: too long\n");	
	break;
      }
    

      kano_log_info("kano-launcher: running kill cmd [%s]\n",kill_cmd);
      err=system(kill_cmd);
      if(err){
	kano_log_error("kano-launcher: error (%d) from kill command:[%s]\n",err,kill_cmd);	
      }
    }while(0);  
  
    err = umount(my_contfile);
    if(err)
      kano_log_error("kano-launcher: error (%d) from unmounting :[%s]\n",err,my_contfile);

    // try and delete it anyway...
    err = unlink(my_contfile);
    if(err)
	kano_log_error("kano-launcher: error (%d) from removing :[%s]\n",err,my_contfile);
      
  }while(0);
}

void kill_containers(){
  if(!contdir_set){
    // can't do anything, but keep going and launch the app
    return;
  }
  
  DIR *conf_dir=opendir(contdir);
  if(!conf_dir) {
    kano_log_error("kano-launcher: did not find container dir\n");
    return;
  }
  struct dirent *d;
  
  while((d=readdir(conf_dir))){
    if(d->d_name[0]!='.'){
      kano_log_debug("kano-launcher: killing container %s\n",d->d_name);
      kill_container(d->d_name);      
    }
  }
  closedir(conf_dir);


}
// error checking: always try to launch the app, if possible.
// but not if we can't drop root privilege.

int main(int argc, char *argv[]){
  char *homedir=getenv("HOME");
  if(homedir){

    int count=snprintf(contdir, STRING_SIZE,"%s/.kano-app-containers",homedir);
    if(count!=0 && count != STRING_SIZE){

      int err=mkdir(contdir, S_IWUSR | S_IRUSR | S_IXUSR);

      if(!err || errno==EEXIST)
      contdir_set=1;
    }
  }
  
  char *command=NULL;
  char *preset=NULL;
  if(argc<2){
    // error msg
    exit(1);
  }
  if(argc>=2){
    command=argv[1];
  }
  if(argc>2){
    preset=argv[2];
  }
    
  // get real user ids so we can use them to drop privilege
  uid=getuid();
  gid=getgid();

  
  config conf={ true, true, "" };
  bool pi2=is_pi2();
  bool conf_matched=0;

  int err=get_config(preset,command,&conf_matched,&conf);
  if(err)
    kano_log_warning("kano-launcher: error reading config\n");

  // don't bother doing containerisation on the pi2
  bool do_container = conf_matched && !pi2;


  if(do_container && !conf.no_kill){
    kill_containers();
  }
  run_container(do_container,command);
  if(conf.extra_cmd[0]) {
      run_container(do_container,conf.extra_cmd);
  }
  
  return 0;
}
