#!/usr/bin/env python

# paths.py
#
# Copyright (C) 2014-2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

'''
Discovers and exposes the absolute pathnames for common_css_dir and common_images_dir
'''

import os

# setting up directories
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# media dir
media_local = os.path.join(dir_path, 'media')
media_usr = '/usr/share/kano/media'

if os.path.exists(media_local):
    common_media_dir = media_local
elif os.path.exists(media_usr):
    common_media_dir = media_usr
else:
    raise Exception('Neither local nor usr media dir found!')

common_css_dir = os.path.join(common_media_dir, 'CSS')
common_images_dir = os.path.join(common_media_dir, 'images')

DNS_FILE = '/etc/resolvconf/resolv.conf.d/base'
DNS_INTERFACES_FILE = '/etc/resolvconf/interface-order'
DNS_INTERFACES_BACKUP_FILE = '/etc/resolvconf/interface-order.backup'
SUPPLICANT_LOGFILE = '/var/log/kano_wpa.log'
SUPPLICANT_CONFIG='/etc/wpa_supplicant/wpa_supplicant.conf'
INTERNET_UP_FILE = '/var/run/internet_monitor'
KANO_CONNECT_PIDFILE = '/var/run/kano-connect.pid'
