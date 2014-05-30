# kano.logger
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import sys
import re
import json
import time
from kano.colours import decorate_string, decorate_with_preset

LOG_ENV = "LOG_LEVEL"
DEBUG_ENV = "DEBUG_LEVEL"
SYSTEM_LOGS_DIR = "/var/log/kano/"
USER_LOGS_DIR = os.path.expanduser("~/.kano-logs/")


def normalise_level(level):
    if level == None:
        return "none"

    level = level.lower()
    if level == "none"[0:len(level)]:
        return "none"
    elif level == "error"[0:len(level)]:
        return "error"
    elif level == "warning"[0:len(level)]:
        return "warning"
    elif level == "info"[0:len(level)]:
        return "info"
    elif level == "debug"[0:len(level)]:
        return "debug"


def get_log_level():
    return normalise_level(os.environ.get(LOG_ENV))


def get_debug_level():
    return normalise_level(os.environ.get(DEBUG_ENV))


levels = {
    "none": 0,
    "error": 1,
    "warning": 2,
    "info": 3,
    "debug": 4
}
log_level = levels[get_log_level()]
debug_level = levels[get_debug_level()]

log_file = None
app_name = None
pid = os.getpid()


def set_app_name(name):
    global app_name, log_file
    app_name = os.path.basename(name.strip()).lower().replace(" ", "_")
    if log_file != None:
        log_file.close()
        log_file = None


def write(msg, **kwargs):
    lname = "info"
    if "level" in kwargs:
        lname = normalise_level(kwargs["level"])

    level = levels[lname]

    log = {}
    if level > 0 and (level <= log_level or level <= debug_level):
        if app_name == None:
            set_app_name(sys.argv[0])

        log["time"] = time.time()
        log["pid"] = pid
        log.update(kwargs)
        log["message"] = msg
        log["level"] = lname

        if level <= log_level:
            if log_file == None:
                _init_log_file()

            log_file.write("{}\n".format(json.dumps(log)))

        if level <= debug_level:
            print "{}[{}] {} {}".format(
                app_name,
                decorate_string(pid, "yellow"),
                decorate_with_preset(log["level"], log["level"]),
                log["message"]
            )


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
