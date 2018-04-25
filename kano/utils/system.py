# system.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utilities related to the operating system

import os


def get_debian_version(stamp_file='/etc/debian_version'):
    '''
    Returns Debian version number from official stamp file
    '''
    try:
        with open(stamp_file) as f:
            osversion = f.read().strip()

        major, minor = osversion.split('.')
        return major, minor
    except Exception:
        return None, None


def is_jessie():
    '''
    Returns True if running Debian Jessie
    '''
    major, minor = get_debian_version()
    return major == '8'


def is_stretch():
    '''
    Returns True if runing Debian Stretch
    '''
    major, minor = get_debian_version()
    return major == '9'


def is_systemd():
    '''
    returns True if we are in a systemd environment - Debian Jessie
    '''
    try:
        return os.readlink('/sbin/init') == '/lib/systemd/systemd'
    except Exception:
        return False
