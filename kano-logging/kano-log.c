// kano-log.c
//
// Copyright (C) 2015 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// Implementation of logging

// Currently uses syslog, needs to change to use out log files
#include <syslog.h>
#include <stdarg.h>
#include <syslog.h>

void kano_log_error(char *msg,...){
  va_list ap;
  va_start(ap,msg);
  vsyslog(LOG_USER | LOG_ERR, msg, ap);
  va_end(ap);
}
void kano_log_warning(char *msg,...){
  va_list ap;
  va_start(ap,msg);
  vsyslog(LOG_USER | LOG_WARNING, msg, ap);
  va_end(ap);
}
void kano_log_info(char *msg,...){
  va_list ap;
  va_start(ap,msg);
  vsyslog(LOG_USER | LOG_INFO, msg, ap);
  va_end(ap);
}
void kano_log_debug(char *msg,...){
  va_list ap;
  va_start(ap,msg);
  vsyslog(LOG_USER | LOG_ERR, msg, ap);
  va_end(ap);
}


