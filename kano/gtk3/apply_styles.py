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


# Apply the general CSS files to the screen
def apply_common_to_screen():
    apply_colours_to_screen()
    apply_base_to_screen()


# This applies the colour variable names to the screen
def apply_colours_to_screen():
    apply_styling_to_screen(common_css_dir + "/colours.css", "APPLICATION")


# This applies the base styling of the widgets to the screen
def apply_base_to_screen():
    apply_styling_to_screen(common_css_dir + "/widgets.css", "APPLICATION")


# Apply the styling from a filename to the screen
def apply_styling_to_screen(css_file, priority="USER"):
    css = Gtk.CssProvider()

    if not os.path.exists(css_file):
        sys.exit(css_file + ' CSS file missing!')

    css.load_from_path(css_file)

    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()

    if priority == "FALLBACK":
        gtk_priority = Gtk.STYLE_PROVIDER_PRIORITY_FALLBACK
    elif priority == "THEME":
        gtk_priority = Gtk.STYLE_PROVIDER_PRIORITY_THEME
    elif priority == "SETTINGS":
        gtk_priority = Gtk.STYLE_PROVIDER_PRIORITY_SETTINGS
    elif priority == "APPLICATION":
        gtk_priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    elif priority == "USER":
        gtk_priority = Gtk.STYLE_PROVIDER_PRIORITY_USER

    styleContext.add_provider_for_screen(screen, css, gtk_priority)


# Apply the styling from a CSS file to a specific widget
def apply_styling_to_widget(widget, path):

    if not os.path.exists(path):
        sys.exit('{} CSS file missing!'.format(path))

    provider = Gtk.CssProvider()
    provider.load_from_path(path)
    styleContext = widget.get_style_context()
    styleContext.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)


# Apply the colour variable names to the widget (useful if you want to refer to kano_green)
def apply_colours_to_widget(widget):
    path = os.path.join(common_css_dir, "colours.css")
    apply_styling_to_widget(widget, path)


# Apply the general styling of all the widgets to the widget (TODO: is this needed?)
def apply_base_to_widget(widget):
    path = os.path.join(common_css_dir, "common.css")
    apply_styling_to_widget(widget, path)
