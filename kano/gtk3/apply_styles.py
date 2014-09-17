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


def apply_styles_to_screen():
    apply_colours_to_screen()
    apply_common_to_screen()


def apply_colours_to_screen():
    apply_styling_to_screen(common_css_dir + "/colours.css")


def apply_common_to_screen():
    apply_styling_to_screen(common_css_dir + "/common.css")


def apply_styling_to_screen(path):
    css = Gtk.CssProvider()

    css_file = os.path.join(path)
    if not os.path.exists(css_file):
        sys.exit(path + ' CSS file missing!')

    css.load_from_path(css_file)

    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, css, Gtk.STYLE_PROVIDER_PRIORITY_USER)


def apply_styling_to_widget(widget, path):
    provider = Gtk.CssProvider()
    provider.load_from_path(path)
    styleContext = widget.get_style_context()
    styleContext.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)


def apply_colours_to_widget(widget):
    path = os.path.join(common_css_dir, "colours.css")
    apply_styling_to_widget(widget, path)


def apply_common_to_widget(widget):
    path = os.path.join(common_css_dir, "common.css")
    apply_styling_to_widget(widget, path)
