# user.py
#
# Copyright (C) 2014-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utilities related to linux users


import os
import sys
import pwd
import getpass


def get_user_getpass():
    return getpass.getuser()


def get_user():
    return os.environ.get('LOGNAME', '')


def get_user_unsudoed():
    if 'SUDO_USER' in os.environ:
        return os.environ['SUDO_USER']
    elif 'LOGNAME' in os.environ:
        return os.environ['LOGNAME']
    else:
        return 'root'


def get_home():
    return os.path.expanduser('~')


def get_home_by_username(username):
    return pwd.getpwnam(username).pw_dir


def get_all_home_folders(root=False, skel=False):
    home = '/home'
    folders = [os.path.join(home, f) for f in os.listdir(home)]
    if root:
        folders += ['/root']
    if skel:
        folders += ['/etc/skel']
    return folders


def enforce_root(msg):
    if os.getuid() != 0:
        sys.stderr.write(msg.encode('utf-8') + "\n")
        sys.exit(1)
