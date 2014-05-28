#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

# setting up directories
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# media dir
css_local = os.path.join(dir_path, 'CSS')
css_usr = '/usr/share/kano/CSS'

if os.path.exists(css_local):
    common_css_dir = css_local
elif os.path.exists(css_usr):
    common_css_dir = css_usr
else:
    raise Exception('Neither local nor usr css dir found!')
