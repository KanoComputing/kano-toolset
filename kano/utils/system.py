# system.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utilities related to the operating system


import os

kanux_stamp_file='/boot/kanux_stamp'


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


def get_kano_version_stamp():
    '''
    Returns the raw string from the version stamp file
    Kanux version stamps come in this form:
       " Sat Sep  3 03:18:24 BST 2016 Kanux-Beta-v3.5.0-jessie"
    '''
    with open(kanux_stamp_file, 'r') as f:
        return f.read().strip(' \n')


def get_kano_version_date():
    '''
    Returns the date this version was built
    '''
    try:
        # FIXME: This is a little obscure
        return get_kano_version_stamp().split('-')[0].strip('Kanux')
    except:
        return 'n/a'


def get_kano_version_number():
    '''
    returns the Kano OS version number
    '''
    stamp=get_kano_version_stamp().split('-')
    for item in stamp:
        if item.startswith('v'):
            return item

    return 'n/a'


def is_kano_public_release():
    '''
    returns True if this Kano system is a public release version
    '''
    return 'release' in get_kano_version_stamp().split('-')


def is_kano_internal_development():
    '''
    returns True if this Kano system is an internal development version
    '''
    return not is_kano_public_release()
