#!/usr/bin/env python

# kano_scrolled_window.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Create a green button with white text inside

from gi.repository import Gtk
from kano.paths import common_css_dir
import os
import sys


class ScrolledWindow(Gtk.ScrolledWindow):
    def __init__(self, hexpand=None, vexpand=None):
        scrollbar_css = Gtk.CssProvider()
        css_file = os.path.join(common_css_dir, 'scrollbar.css')
        if not os.path.exists(css_file):
            sys.exit('CSS file missing!')
        colour_css = Gtk.CssProvider()
        colour_file = os.path.join(common_css_dir, 'colours.css')
        if not os.path.exists(colour_file):
            sys.exit('CSS file missing!')
        colour_css.load_from_path(colour_file)
        scrollbar_css.load_from_path(css_file)

        Gtk.ScrolledWindow.__init__(self, hexpand=hexpand, vexpand=vexpand)

        styleContext = self.get_style_context()
        styleContext.add_provider(colour_css, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        styleContext.add_provider(scrollbar_css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        for bar in [self.get_vscrollbar(), self.get_hscrollbar()]:
            style = bar.get_style_context()
            style.add_provider(colour_css, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            style.add_provider(scrollbar_css, Gtk.STYLE_PROVIDER_PRIORITY_USER)
