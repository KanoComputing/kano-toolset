#!/usr/bin/env python

# kano.logger
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import sys
import json
import time

CONF = "/etc/debug"
SYSTEM_LOGS_DIR = "/var/log/kano/"
USER_LOGS_DIR = os.path.expanduser("~/.logs/")

logging_enabled = False
log_file = None
app_name = None
pid = os.getpid()


def enable():
    global logging_enabled
    logging_enabled = True


def disable():
    global logging_enabled, log_file
    if log_file:
        log_file.close()
        log_file = None

    logging_enabled = False


def set_app_name(name):
    global app_name
    app_name = os.path.basename(name.strip()).lower().replace(" ", "_")
    if log_file != None:
        _init_log_file()

def set_pid(p):
    global pid
    pid = p


def write(msg, data=None):
    if logging_enabled == None:
        if os.path.exists(CONF):
            enable()

    if logging_enabled:
        if log_file == None:
            _init_log_file()

        if app_name == None:
            set_app_name(sys.argv[0])

        log = data.copy() if data != None else {}
        log["message"] = msg
        log["time"] = time.time()
        log["pid"] = pid
        log_file.write("{}\n".format(json.dumps(log)))


def _init_log_file():
    global log_file

    if log_file != None:
        log_file.close()

    logs_dir = USER_LOGS_DIR
    if os.getuid() == 0:
        logs_dir = os.path.expanduser(SYSTEM_LOGS_DIR)

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    log_file = open("{}/{}.log".format(logs_dir, app_name), "a")
