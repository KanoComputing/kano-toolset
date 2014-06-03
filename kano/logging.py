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
    ENV_CONF = "/etc/environment"

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

    def force_log_level(self, level):
        level_no = self.LEVELS[self.normalise_level(level)]
        if self._log_level < level_no:
            self._log_level = level_no

    def force_debug_level(self, level):
        level_no = self.LEVELS[self.normalise_level(level)]
        if self._debug_level < level_no:
            self._debug_level = level_no

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
        if level > 0 and (level <= self._log_level or level <= self._debug_level):
            if self._app_name == None:
                self.set_app_name(sys.argv[0])

            lines = msg.strip().split("\n")
            for line in lines:
                log = {}
                log["time"] = time.time()
                log["pid"] = self._pid
                log.update(kwargs)
                log["message"] = line
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

def set_system_log_level(lvl):
    _set_system_env_var(logger.LOG_ENV, lvl)


def set_system_debug_level(lvl):
    _set_system_env_var(logger.DEBUG_ENV, lvl)


def _set_system_env_var(var, val):
    output = []
    var_replaced = False
    if os.path.exists(logger.ENV_CONF):
        with open(logger.ENV_CONF, "r") as f:
            for line in f:
                if re.match(var, line):
                    output.append("{}={}\n".format(var, val))
                    var_replaced = True
                else:
                    output.append(line)

    if not os.path.exists(logger.ENV_CONF) or not var_replaced:
        output.append("{}={}\n".format(var, val))

    with open(logger.ENV_CONF, "w") as f:
        for line in output:
            f.write(line)

def read_logs(app=None):
    data = {}
    for d in [logger.USER_LOGS_DIR, logger.SYSTEM_LOGS_DIR]:
        if os.path.isdir(d):
            for log in os.listdir(d):
                log_path = os.path.join(d, log)
                with open(log_path, "r") as f:
                    data[log_path] = map(json.loads, f.readlines())

    return data

def cleanup(app=None):
    for d in [logger.USER_LOGS_DIR, logger.SYSTEM_LOGS_DIR]:
        if os.path.isdir(d):
            for log in os.listdir(d):
                log_path = os.path.join(d, log)
                __tail_log_file(log_path, 10)

def __tail_log_file(file_path, length):
    data = None
    with open(file_path, "r") as f:
        data = f.readlines()

    print len(data)
    if len(data) <= length:
        return

    print len(data[(len(data) - length):])
    with open(file_path, "w") as f:
        f.write("".join(data[(len(data) - length):]))
