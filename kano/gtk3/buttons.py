#!/usr/bin/env python

# buttons.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.gtk3 import cursor
from kano.paths import common_css_dir
import os
import sys


class GenericButton(Gtk.Button):
    def __init__(self, text=""):

        Gtk.Button.__init__(self)

        self.button_css = Gtk.CssProvider()
        css_file = os.path.join(common_css_dir, 'buttons.css')
        if not os.path.exists(css_file):
            sys.exit('CSS file missing!')
        self.button_css.load_from_path(css_file)

        self.colour_css = Gtk.CssProvider()
        colour_file = os.path.join(common_css_dir, 'colours.css')
        if not os.path.exists(colour_file):
            sys.exit('CSS file missing!')
        self.colour_css.load_from_path(colour_file)

        style_context = self.get_style_context()
        style_context.add_provider(self.button_css, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context.add_provider(self.colour_css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.label = Gtk.Label(text)
        self.add(self.label)
        style = self.label.get_style_context()
        style.add_provider(self.button_css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        cursor.attach_cursor_events(self)

    def set_label(self, text):
        self.label.set_text(text)


class KanoButton(GenericButton):
    def __init__(self, text="", color="green"):
        # Keep this updated - useful for set_color function
        self.available_colors = ["orange", "green", "red", "grey"]

        # Create button
        GenericButton.__init__(self, text)

        style_context = self.get_style_context()
        style_context.add_class("kano_button")
        style_context.add_class(color + "_background")

        self.align = None
        cursor.attach_cursor_events(self)

    def pack(self):
        self.box = Gtk.Box()
        self.box.add(self)

    # Pakcing in a box and within an Alignment
    def pack_and_align(self):
        # This stops the button resizing to fit the size of it's container
        self.box = Gtk.Box()
        self.box.add(self)
        self.props.halign = Gtk.Align.CENTER
        self.box.props.halign = Gtk.Align.CENTER

        # This allows us to set our padding
        self.align = Gtk.Alignment()
        self.align.add(self.box)

    def set_padding(self, top, bottom, left, right):
        if self.align is not None:
            self.align.set_padding(top, bottom, left, right)

    def set_color(self, color):
        for c in self.available_colors:
            self.get_style_context().remove_class(c + "_background")
        self.get_style_context().add_class(color + "_background")


class OrangeButton(GenericButton):
    def __init__(self, text=""):

        # Create button
        GenericButton.__init__(self, text)
        self.get_style_context().add_class("small_orange_button")
