#!/usr/bin/env python

# buttons.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Gdk
from kano.gtk3 import cursor
from kano.paths import common_css_dir
import os
import sys


class GenericButton(Gtk.Button):
    def __init__(self, text="", icon_filename=""):

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

        self.internal_box = Gtk.Box(spacing=10)
        self.internal_box.props.halign = Gtk.Align.CENTER
        self.add(self.internal_box)

        if icon_filename:
            self.icon = Gtk.Image.new_from_file(icon_filename)
            self.internal_box.pack_start(self.icon, False, False, 0)
            self.label = Gtk.Label(text)
            self.internal_box.pack_start(self.label, False, False, 0)
        else:
            self.label = Gtk.Label(text)
            self.internal_box.add(self.label)

        style = self.label.get_style_context()
        style.add_provider(self.button_css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        cursor.attach_cursor_events(self)

    def set_label(self, text):
        self.label.set_text(text)

    def get_label(self):
        return self.label.get_text()


class KanoButton(GenericButton):
    def __init__(self, text="", color="green", icon_filename=""):

        # Keep this updated - useful for set_color function
        self.available_colors = ["orange", "green", "red", "grey", "blue"]

        self.spinner = Gtk.Spinner()
        self.is_spinning = False

        # Create button
        GenericButton.__init__(self, text, icon_filename)

        style_context = self.get_style_context()
        style_context.add_class("kano_button")
        style_context.add_class("kano_button_padding")
        style_context.add_class(color + "_background")

        self.align = None
        cursor.attach_cursor_events(self)

    def pack(self):
        self.box = Gtk.Box()
        self.box.add(self)

    # Pakcing in a box and within an Alignment
    def pack_and_align(self):

        # This stops the button resizing to fit the size of its container
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

    def set_margin(self, top_margin, right_margin, bottom_margin, left_margin):
        self.set_margin_left(left_margin)
        self.set_margin_right(right_margin)
        self.set_margin_top(top_margin)
        self.set_margin_bottom(bottom_margin)

    # Threading should be handled by each individual program, so we don't get memory leaks from
    # two sets of initialisation of GObject.threads.init()
    def start_spinner(self):
        self.remove(self.internal_box)
        self.add(self.spinner)

        # Stops background going grey on making kano button insensitive,
        # and controls styling of spinner
        self.get_style_context().add_class("loading_kano_button")

        # force change of class? This may not be neccessary
        self.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse("green"))

        self.set_sensitive(False)
        self.show_all()
        self.is_spinning = True
        self.spinner.start()

    def stop_spinner(self):
        self.spinner.stop()
        self.remove(self.spinner)
        self.add(self.internal_box)
        self.set_sensitive(True)
        self.is_spinning = False


class OrangeButton(GenericButton):
    def __init__(self, text=""):

        # Create button
        GenericButton.__init__(self, text)
        self.get_style_context().add_class("small_orange_button")


class KanoButtonBox(Gtk.ButtonBox):
    def __init__(self, button1_text, orange_button_text=""):

        Gtk.ButtonBox.__init__(self, spacing=10)
        self.set_layout(Gtk.ButtonBoxStyle.SPREAD)

        self.kano_button = KanoButton(button1_text)

        if orange_button_text:
            self.orange_button = OrangeButton(orange_button_text)
            self.pack_start(self.orange_button, False, False, 0)
            self.pack_start(self.kano_button, False, False, 0)

            # The empty label is to centre the kano_button
            self.label = Gtk.Label("    ")
            self.pack_start(self.label, False, False, 0)
        else:
            self.pack_start(self.kano_button, False, False, 0)
