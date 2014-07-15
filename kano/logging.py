# kano.logging
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import sys
import re
import pwd
import grp
import json
import time
import yaml
from kano.colours import decorate_string_only_terminal, decorate_with_preset
from kano.utils import get_home_by_username

LOG_ENV = "LOG_LEVEL"
OUTPUT_ENV = "OUTPUT_LEVEL"
SYSTEM_LOGS_DIR = "/var/log/kano/"

# The length to which will the log files be cut to when cleaned up
TAIL_LENGTH = 500

# get_user_unsudoed() cannot be used due to a circular dependency
is_sudoed = 'SUDO_USER' in os.environ
usr = os.getenv("SUDO_USER") if is_sudoed else pwd.getpwuid(os.getuid())[0]

try:
    home_folder = get_home_by_username(usr)
except KeyError:  # user doesn't exist
    if is_sudoed:
        # something weird happened with sudo
        # fall back to the root user
        usr = "root"
        home_folder = "/root/"
    else:
        raise

USER_LOGS_DIR = os.path.join(home_folder, '.kano-logs')

CONF_FILE = "/etc/kano-logs.conf"

LEVELS = {
    "none": 0,
    "error": 1,
    "warning": 2,
    "info": 3,
    "debug": 4
}


def normalise_level(level):
    if level is None:
        return "none"

    level = level.lower()
    for l in LEVELS.iterkeys():
        if level == l[0:len(level)]:
            return l

    return "none"


class Logger:
    def __init__(self):
        self._log_file = None
        self._app_name = None
        self._pid = os.getpid()

        log = os.getenv(LOG_ENV)
        if log is not None:
            log = normalise_level(log)
        self._cached_log_level = log

        output = os.getenv(OUTPUT_ENV)
        if output is not None:
            output = normalise_level(output)
        self._cached_output_level = output

    def _load_conf(self):
        conf = None
        if os.path.exists(CONF_FILE):
            with open(CONF_FILE, "r") as f:
                conf = yaml.load(f)

        if conf is None:
            conf = {}

        if "log_level" not in conf:
            conf["log_level"] = "none"

        if "output_level" not in conf:
            conf["output_level"] = "none"

        if self._cached_log_level is None:
            self._cached_log_level = normalise_level(conf["log_level"])

        if self._cached_output_level is None:
            self._cached_output_level = normalise_level(conf["output_level"])

    def get_log_level(self):
        if self._cached_log_level is None:
            self._load_conf()

        return self._cached_log_level

    def get_output_level(self):
        if self._cached_output_level is None:
            self._load_conf()

        return self._cached_output_level

    def force_log_level(self, level):
        normalised = normalise_level(level)
        if not self._cached_log_level or \
           LEVELS[self._cached_log_level] < LEVELS[normalised]:
            self._cached_log_level = normalised

    def force_debug_level(self, level):
        normalised = normalise_level(level)
        if not self._cached_output_level or \
           LEVELS[self._cached_output_level] < LEVELS[normalised]:
            self._cached_output_level = normalised

    def set_app_name(self, name):
        self._app_name = os.path.basename(name.strip()).lower().replace(" ", "_")
        if self._log_file is not None:
            self._log_file.close()
            self._log_file = None

    def write(self, msg, **kwargs):
        lname = "info"
        if "level" in kwargs:
            lname = normalise_level(kwargs["level"])

        level = LEVELS[lname]
        sys_log_level = LEVELS[self.get_log_level()]
        sys_output_level = LEVELS[self.get_output_level()]

        if level > 0 and (level <= sys_log_level or level <= sys_output_level):
            if self._app_name is None:
                self.set_app_name(sys.argv[0])

            lines = str(msg).strip().split("\n")
            for line in lines:
                log = {}
                log["time"] = time.time()
                log["pid"] = self._pid
                log.update(kwargs)
                log["message"] = line
                log["level"] = lname

                if level <= sys_log_level:
                    if self._log_file is None:
                        self._init_log_file()
                    self._log_file.write("{}\n".format(json.dumps(log)))

                if level <= sys_output_level:
                    print "{}[{}] {} {}".format(
                        self._app_name,
                        decorate_string_only_terminal(self._pid, "yellow"),
                        decorate_with_preset(log["level"], log["level"], True),
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
        if self._log_file is not None:
            self._log_file.close()

        if os.getuid() == 0 and not is_sudoed:
            logs_dir = SYSTEM_LOGS_DIR
        else:
            logs_dir = USER_LOGS_DIR

        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

            # Fix permissions in case we need to create the dir with sudo
            if is_sudoed:
                uid = pwd.getpwnam(usr).pw_uid
                gid = grp.getgrnam(usr).gr_gid
                os.chown(logs_dir, uid, gid)

        log_fn = "{}/{}.log".format(logs_dir, self._app_name)

        # Fix permissions in case we need to create the file with sudo
        if not os.path.isfile(log_fn) and is_sudoed:
            # touch
            with open(log_fn, 'a'):
                pass

            uid = pwd.getpwnam(usr).pw_uid
            gid = grp.getgrnam(usr).gr_gid
            os.chown(log_fn, uid, gid)

        self._log_file = open("{}/{}.log".format(logs_dir, self._app_name), "a")

logger = Logger()


def set_system_log_level(lvl):
    _set_conf_var("log_level", lvl)


def set_system_output_level(lvl):
    _set_conf_var("output_level", lvl)


def _set_conf_var(var, value):
    conf = None
    if os.path.isfile(CONF_FILE):
        with open(CONF_FILE, "r") as f:
            conf = yaml.load(f)
    if conf is None:
        conf = {}

    conf[var] = normalise_level(str(value))

    with open(CONF_FILE, "w") as f:
        f.write(yaml.dump(conf, default_flow_style=False))


def read_logs(app=None):
    data = {}
    for d in [USER_LOGS_DIR, SYSTEM_LOGS_DIR]:
        if os.path.isdir(d):
            for log in os.listdir(d):
                if app is None or re.match("^{}\.log".format(app), log):
                    log_path = os.path.join(d, log)
                    with open(log_path, "r") as f:
                        data[log_path] = map(json.loads, f.readlines())

    return data


def cleanup(app=None, line_limit=TAIL_LENGTH):
    dirs = [USER_LOGS_DIR]
    if os.getuid() == 0:
        dirs.append(SYSTEM_LOGS_DIR)

    for d in dirs:
        if os.path.isdir(d):
            for log in os.listdir(d):
                if app is None or re.match("^{}\.log".format(app), log):
                    log_path = os.path.join(d, log)
                    try:
                        __tail_log_file(log_path, line_limit)
                    except IOError:
                        pass


def __tail_log_file(file_path, length):
    data = None
    with open(file_path, "r") as f:
        data = f.readlines()

    if len(data) <= length:
        return

    with open(file_path, "w") as f:
        f.write("".join(data[(len(data) - length):]))
