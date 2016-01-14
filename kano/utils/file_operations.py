# file_operations.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import os
import re
import pwd
import grp
import shutil
import json
import fcntl

from kano.utils.user import get_user_unsudoed
from kano.utils.shell import run_cmd


def read_file_contents(path):
    if os.path.exists(path):
        with open(path) as infile:
            return infile.read().strip()


def write_file_contents(path, data):
    with open(path, 'w') as outfile:
        outfile.write(data)


def read_file_contents_as_lines(path):
    if os.path.exists(path):
        with open(path) as infile:
            content = infile.readlines()
            lines = [line.strip() for line in content]
            return lines


def delete_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def list_dir(dir_path):
    if os.path.exists(dir_path):
        return os.listdir(dir_path)

    return list()


def chown_path(path, user=None, group=None):
    user_unsudoed = get_user_unsudoed()
    if not user:
        user = user_unsudoed
    if not group:
        group = user_unsudoed
    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid
        os.chown(path, uid, gid)
    except KeyError as e:
        from kano.logging import logger
        logger.error(
            'user {} or group {} do not match with existing'.format(user, group))
        ret_val = False
    except OSError as e:
        from kano.logging import logger
        logger.error(
            'Error while trying to chown, root priviledges needed {}'.format(e))
        ret_val = False
    else:
        ret_val = True
    return ret_val


def read_json(filepath, silent=True):
    try:
        return json.loads(read_file_contents(filepath))
    except Exception:
        if not silent:
            raise


def write_json(filepath, data, prettyprint=False, sort_keys=True):
    with open(filepath, 'w') as outfile:
        json.dump(data, outfile, indent=2, sort_keys=sort_keys)
    if prettyprint:
        _, _, rc = run_cmd('which underscore')
        if rc == 0:
            cmd = 'underscore print -i {filepath} -o {filepath}'.format(filepath=filepath)
            run_cmd(cmd)


class open_locked(file):
    """ A version of open with an exclusive lock to be used within
        controlled execution statements.
    """
    def __init__(self, *args, **kwargs):
        """
        pass optional nonblock=True for nonblocking behavior
        """

        # we need to process 'nonblock' before calling
        # super().__init__ because that does not know about 'nonblock'
        mode = fcntl.LOCK_EX
        if kwargs.get('nonblock') is not None:
            mode = mode | fcntl.LOCK_NB
            del kwargs['nonblock']

        super(open_locked, self).__init__(*args, **kwargs)
        fcntl.flock(self, mode)


def sed(pattern, replacement, file_path, use_regexp=True):
    """ Search and replace a pattern in a file.

    The search happens line-by-line, multiline patterns won't work

    :param pattern: a regular expression to search for
    :param replacement: the replacement string
    :param file_path: location of the file to process
    :returns: number of lines changed
    :raises IOError: File doesn't exist
    """

    changed = 0

    with open(file_path, "r") as file_handle:
        lines = file_handle.readlines()

    with open(file_path, "w") as file_handle:
        for line in lines:
            if use_regexp:
                modified_line = re.sub(pattern, replacement, line)
            else:
                modified_line = line.replace(pattern, replacement)

            file_handle.write(modified_line)

            if line != modified_line:
                changed += 1

    return changed
