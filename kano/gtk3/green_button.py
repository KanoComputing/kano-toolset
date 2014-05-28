#!/usr/bin/env python

# green_button.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Create a green button with white text inside

from gi.repository import Gtk, Gdk
from kano.gtk3 import cursor
from kano.paths import common_css_dir
import os
import sys


class GreenButton(Gtk.Button):
    def __init__(self, text=""):
        print "helllooooooo"
        cssProvider = Gtk.CssProvider()
        button_css = os.path.join(common_css_dir, 'buttons.css')
        if not os.path.exists(button_css):
            sys.exit('CSS file missing!')
        cssProvider.load_from_path(button_css)
        print button_css

        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # Create button
        Gtk.Button.__init__(self)
        self.set_label(text)
        self.get_style_context().add_class("green_button")

        # This stops the button resizing to fit the size of it's container
        self.box = Gtk.Box()
        self.box.add(self)
        self.props.halign = Gtk.Align.CENTER
        self.box.props.halign = Gtk.Align.CENTER

        # This allows us to set our padding
        self.align = Gtk.Alignment()
        self.align.add(self.box)

        cursor.attach_cursor_events(self)

    def set_padding(self, top, bottom, left, right):
        self.align.set_padding(top, bottom, left, right)
