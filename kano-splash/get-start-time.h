/* get-start-time.h
 *
 * Copyright (C) 2015 Kano Computing Ltd.
 * License: http://opensource.org/licenses/MIT
 * 
 * This file exports a function for extracting a process starttime from proc.
 * The idea is to avoid sending signals to a process which has obtained the same pid
 * as the one you intended to send it to.
 */

#ifndef GET_START_TIME_H
#define GET_START_TIME_H
/* 
 * Extract process start time from /proc/<pid>/stat 
 * If anything goes wrong, return 0 
 */
unsigned long long get_process_start_time(pid_t pid);

#endif /*GET_START_TIME_H*/
