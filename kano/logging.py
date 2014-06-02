# kano.logging
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

class Logger:
    LOG_ENV = "LOG_LEVEL"
    DEBUG_ENV = "DEBUG_LEVEL"
    SYSTEM_LOGS_DIR = "/var/log/kano/"
    USER_LOGS_DIR = os.path.expanduser("~/.kano-logs/")

    LEVELS = {
        "none": 0,
        "error": 1,
        "warning": 2,
        "info": 3,
        "debug": 4
    }

    def __init__(self):
        self._log_level = self.LEVELS[self.get_log_level()]
        self._debug_level = self.LEVELS[self.get_debug_level()]

        self._log_file = None
        self._app_name = None
        self._pid = os.getpid()

    def get_log_level(self):
        return self.normalise_level(os.environ.get(self.LOG_ENV))


    def get_debug_level(self):
        return self.normalise_level(os.environ.get(self.DEBUG_ENV))


    def set_app_name(self, name):
        self._app_name = os.path.basename(name.strip()).lower().replace(" ", "_")
        if self._log_file != None:
            self._log_file.close()
            self._log_file = None

    def write(self, msg, **kwargs):
        lname = "info"
        if "level" in kwargs:
            lname = self.normalise_level(kwargs["level"])

        level = self.LEVELS[lname]

        log = {}
        if level > 0 and (level <= self._log_level or level <= self._debug_level):
            if self._app_name == None:
                self.set_app_name(sys.argv[0])

            log["time"] = time.time()
            log["pid"] = self._pid
            log.update(kwargs)
            log["message"] = msg
            log["level"] = lname

            if level <= self._log_level:
                if self._log_file == None:
                    self._init_log_file()

                self._log_file.write("{}\n".format(json.dumps(log)))

            if level <= self._debug_level:
                print "{}[{}] {} {}".format(
                    self._app_name,
                    decorate_string(self._pid, "yellow"),
                    decorate_with_preset(log["level"], log["level"]),
                    log["message"]
                )

    def error(self, msg, **kwargs):
        kwargs["level"] = "error"
        self.write(msg, **kwargs)

    def debug(self, msg, **kwargs):
        kwargs["level"] = "debug"
        self.write(msg, **kwargs)

    def warn(self, msg, **kwargs):
        kwargs["level"] = "warn"
        self.write(msg, **kwargs)

    def info(self, msg, **kwargs):
        kwargs["level"] = "info"
        self.write(msg, **kwargs)


    def _init_log_file(self):
        if self._log_file != None:
            self._log_file.close()

        logs_dir = self.USER_LOGS_DIR
        if os.getuid() == 0:
            logs_dir = os.path.expanduser(self.SYSTEM_LOGS_DIR)

        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        self._log_file = open("{}/{}.log".format(logs_dir, self._app_name), "a")

    def normalise_level(self, level):
        if level == None:
            return "none"

        level = level.lower()
        if level == "error"[0:len(level)]:
            return "error"
        elif level == "warning"[0:len(level)]:
            return "warning"
        elif level == "info"[0:len(level)]:
            return "info"
        elif level == "debug"[0:len(level)]:
            return "debug"

        return "none"

logger = Logger()
