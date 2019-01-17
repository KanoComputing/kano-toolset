#!/usr/bin/env python

# __init__.py
#
# Copyright (C) 2014-2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

__author__ = 'Kano Computing Ltd.'
__email__ = 'dev@kano.me'

import os
import sys

DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if DIR_PATH != '/usr':
    sys.path.insert(1, DIR_PATH)
    LOCALE_PATH = os.path.join(DIR_PATH, 'locale')
else:
    LOCALE_PATH = None

import kano_i18n.init
kano_i18n.init.register_domain('kano-toolset', LOCALE_PATH)
