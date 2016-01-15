#!/usr/bin/env python

# buttons.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import sys
from gi.repository import Gtk

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano.gtk3 import cursor
from kano.gtk3.apply_styles import apply_styling_to_widget, apply_colours_to_widget
from kano.paths import common_css_dir


class GenericButton(Gtk.Button):
    def __init__(self, text="", icon_filename=""):

        Gtk.Button.__init__(self)

        apply_colours_to_widget(self)

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

        cursor.attach_cursor_events(self)

    def set_label(self, text):
        self.label.set_text(text)

    def get_label(self):
        return self.label.get_text()


class KanoButton(GenericButton):
    BUTTON_CSS = os.path.join(common_css_dir, 'kano_button.css')
    SPINNER_CSS = os.path.join(common_css_dir, 'spinner.css')

    def __init__(self, text="", color="green", icon_filename=""):

        # Keep this updated - useful for set_color function
        self.available_colors = ["orange", "green", "red", "grey", "blue"]

        # Create button
        GenericButton.__init__(self, text, icon_filename)

        style_context = self.get_style_context()
        style_context.add_class("kano_button")
        style_context.add_class("kano_button_padding")
        style_context.add_class(color + "_background")

        self.align = None
        cursor.attach_cursor_events(self)

        self.add_spinner()

        widgets = [self, self.label]
        for w in widgets:
            apply_colours_to_widget(w)
            apply_styling_to_widget(w, self.BUTTON_CSS)

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
        self.align = Gtk.Alignment(xscale=0, yscale=0)
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

    def add_spinner(self):
        self.spinner = Gtk.Spinner()
        self.spinner.props.active = True
        self.is_spinning = False
        apply_styling_to_widget(self.spinner, self.SPINNER_CSS)

    def start_spinner(self):
        if self.is_spinning:
            return

        # Keep old dimensions with box
        allocation = self.get_allocation()
        self.remove(self.internal_box)
        self.add(self.spinner)
        self.set_size_request(allocation.width, allocation.height)

        # Stops background going grey on making kano button insensitive,
        # and controls styling of spinner
        self.get_style_context().add_class("loading_kano_button")

        self.is_spinning = True
        self.show_all()
        self.spinner.start()

    # Replace content of button with original content and stop spinner spinning
    def stop_spinner(self):
        if not self.is_spinning:
            return

        self.spinner.stop()
        self.remove(self.spinner)
        self.add(self.internal_box)
        self.get_style_context().remove_class("loading_kano_button")
        self.is_spinning = False


class OrangeButton(GenericButton):
    BUTTON_CSS = os.path.join(common_css_dir, 'small_orange_button.css')

    def __init__(self, text=""):

        # Create button
        GenericButton.__init__(self, text)
        apply_styling_to_widget(self, self.BUTTON_CSS)
        apply_styling_to_widget(self.label, self.BUTTON_CSS)

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


# This is a test class to try out different button functions
class TestWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.box = Gtk.Box()
        self.add(self.box)

        colours = ["red", "blue", "green", "orange"]
        for c in colours:
            button = KanoButton("hello", color=c)
            self.box.pack_start(button, False, False, 0)
            button.connect("button-release-event", self.spinner_test)

        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def spinner_test(self, widget, event):
        if widget.is_spinning:
            widget.stop_spinner()
        else:
            widget.start_spinner()
            widget.set_sensitive(False)


if __name__ == "__main__":
    win = TestWindow()
    win.connect("delete-event", Gtk.main_quit)
    Gtk.main()
