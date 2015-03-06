// kano-log.c
//
// Copyright (C) 2015 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// Implementation of logging

// Currently uses syslog, needs to change to use out log files

#ifndef KANO_LOG_H
#define KANO_LOG_H

void kano_log_error(char *msg,...);
void kano_log_warning(char *msg,...);
void kano_log_info(char *msg,...);
void kano_log_debug(char *msg,...);

#endif // KANO_LOG_H
