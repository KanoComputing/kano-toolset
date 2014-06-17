#!/usr/bin/env python

# apply_styles.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This is a function to apply the common styles across a window

import os
import sys
from gi.repository import Gtk, Gdk
from kano.paths import common_css_dir


def apply_styles():
    apply_colours()
    apply_common()


def apply_colours():
    apply_named_style("colours")


def apply_common():
    apply_named_style("common")


def apply_named_style(style_name):
    css = Gtk.CssProvider()

    css_file = os.path.join(common_css_dir, style_name + '.css')
    if not os.path.exists(css_file):
        sys.exit(style_name + 'CSS file missing!')

    css.load_from_path(css_file)

    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, css, Gtk.STYLE_PROVIDER_PRIORITY_USER)
