# file_operations.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utilities relating to file operations


import os
import re
import pwd
import getpass
import grp
import shutil
import json
import fcntl
import errno
import stat
import time

from kano.utils.user import get_user_unsudoed
from kano.utils.shell import run_cmd


class TimeoutException(Exception):
    pass


def get_path_owner(path):
    owner = ''
    try:
        owner = pwd.getpwuid(os.stat(path).st_uid).pw_name
    except (IOError, OSError) as exc_err:
        from kano.logging import logger
        logger.warn(
            "Can't get path owner on {} due to permission/IO issues - {}"
            .format(path, exc_err)
        )

    return owner


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


def empty_directory(dir_path):
    """ This function removes all files and directories from a directory
    without deleting it.
    """
    if not os.path.exists(dir_path):
        from kano.logging import logger
        logger.warn("Can't empty, '{}' it doesn't exist".format(dir_path))
        return False

    if not os.path.isdir(dir_path):
        from kano.logging import logger
        logger.warn("Can't empty, '{}' it isn't a directory".format(dir_path))
        return False

    # If the current user is not the same as path owner we want to stop to
    # prevent silently introducing ownership issues
    if not getpass.getuser() != get_path_owner(dir_path):
        from kano.logging import logger
        logger.warn(
            "Can't empty, '{}' owner is not as current user"
            .format(dir_path)
        )
        return False

    try:
        perm_mask = stat.S_IMODE(os.stat(dir_path).st_mode)
        shutil.rmtree(dir_path, ignore_errors=True)
        os.makedirs(dir_path, mode=perm_mask)
    except (IOError, OSError) as exc_err:
        from kano.logging import logger
        logger.warn(
            "Can't empty, '{}' due to permission/IO issues - {}"
            .format(dir_path, exc_err)
        )
        return False

    return True


def recursively_copy(src, dst):
    src_dir = os.path.abspath(src)
    dest_dir = os.path.abspath(dst)

    if not os.path.isdir(src_dir) or not os.path.isdir(dest_dir):
        from kano.logging import logger
        logger.warn(
            "Can't copy '{}' contents into '{}', one of them is not a dir"
            .format(src_dir, dest_dir)
        )
        return False

    try:
        for root_d, dirs, files in os.walk(src_dir):
            # Firstly create the dirs
            dest_root = os.path.join(
                dest_dir,
                os.path.relpath(root_d, src_dir)
            )
            for dir_n in dirs:
                new_dir = os.path.join(dest_root, dir_n)
                os.mkdir(new_dir)
            # Now deal with the files
            for file_n in files:
                src_file = os.path.join(root_d, file_n)
                new_file = os.path.join(dest_root, file_n)
                shutil.copy(src_file, new_file)
    except (IOError, OSError) as exc_err:
        from kano.logging import logger
        logger.warn(
            "Can't copy '{}' contents into '{}', due to permission/IO - {}"
            .format(src_dir, dest_dir, exc_err)
        )
        return False
    return True


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
        pass optional timeout=seconds for timeout blocking.
         If timeout is exhausted, we raise an exception
        """

        # we need to process 'nonblock' before calling
        # super().__init__ because that does not know about 'nonblock'
        mode = fcntl.LOCK_EX
        if kwargs.get('nonblock') is not None:
            mode = mode | fcntl.LOCK_NB
            del kwargs['nonblock']

        timeout = kwargs.get('timeout')
        if timeout is not None:
            mode = mode | fcntl.LOCK_NB
            del kwargs['timeout']

        super(open_locked, self).__init__(*args, **kwargs)

        def flock_try(self, mode):
            # Try locking a file
            # return True on success, "wait" if it is locked

            try:
                fcntl.flock(self, mode)
            except IOError as e:
                if e.errno == errno.EAGAIN:
                    return "wait"
                raise e
            return True

        if timeout:
            # Lock, or retry until timeout is exhausted
            now = time.clock()
            res = False
            while (time.clock() - now) < timeout:
                res = flock_try(self, mode)
                if res is True:
                    break
            if res is not True:
                raise TimeoutException()
        else:
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
