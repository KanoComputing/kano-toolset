# system.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import os


def is_jessie():
    '''
    Returns True if /etc/debian_version tells us
    we are running in a Debian Jessie OS.
    '''
    jessie_found = False

    try:
        with open('/etc/debian_version') as f:
            osversion = f.read().strip()

        major, dummy_minor = osversion.split('.')
        if major == '8':
            jessie_found = True
    except Exception:
        pass

    return jessie_found


def is_systemd():
    '''
    returns True if we are in a systemd environment - Debian Jessie
    '''
    try:
        return os.readlink('/sbin/init') == '/lib/systemd/systemd'
    except Exception:
        return False
