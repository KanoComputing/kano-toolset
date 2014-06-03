#!/usr/bin/env python

# top_bar.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the (pretend) top window bar.

from gi.repository import Gtk, Gdk
from kano.gtk3 import icons
from kano.gtk3.cursor import attach_cursor_events
from kano.paths import common_css_dir
import os
import sys

TOP_BAR_HEIGHT = 44
SPACE_TAKEN = 150
HEADER_SPACE = 25


class TopBar(Gtk.EventBox):
    def __init__(self, title, window_width=-1):

        cssProvider = Gtk.CssProvider()
        top_bar_css = os.path.join(common_css_dir, 'top_bar.css')
        if not os.path.exists(top_bar_css):
            sys.exit('CSS file missing!')
        cssProvider.load_from_path(top_bar_css)

        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        Gtk.EventBox.__init__(self)
        self.set_size_request(window_width, TOP_BAR_HEIGHT)
        background_style = self.get_style_context()
        background_style.add_class('top_bar_container')

        self.height = TOP_BAR_HEIGHT

        self.header = Gtk.Label(title)
        self.header.get_style_context().add_class("top_bar_title")
        print window_width
        if window_width == -1:
            self.align_header = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1, yscale=1)
        else:
            self.align_header = Gtk.Alignment(xalign=0, yalign=0.5, xscale=0, yscale=0)
            padding_left = (window_width - SPACE_TAKEN) / 2 - HEADER_SPACE
            padding_right = (window_width - SPACE_TAKEN) / 2 + HEADER_SPACE
            self.align_header.set_padding(0, 0, padding_left, padding_right)

        self.align_header.add(self.header)

        # Icons of the buttons
        self.pale_prev_arrow = icons.set_from_name("pale_left_arrow")
        self.pale_next_arrow = icons.set_from_name("pale_right_arrow")
        self.dark_prev_arrow = icons.set_from_name("dark_left_arrow")
        self.dark_next_arrow = icons.set_from_name("dark_right_arrow")
        self.cross = icons.set_from_name("cross")

        # Prev Button
        self.prev_button = Gtk.Button()
        self.prev_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        self.prev_button.set_can_focus(False)
        self.prev_button.get_style_context().add_class("top_bar_button")
        self.prev_button.set_image(self.pale_prev_arrow)

        # Next button
        self.next_button = Gtk.Button()
        self.next_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        self.next_button.set_can_focus(False)
        self.next_button.get_style_context().add_class("top_bar_button")
        self.next_button.set_image(self.pale_next_arrow)

        # Close button
        self.close_button = Gtk.Button()
        self.close_button.set_image(self.cross)
        self.close_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        self.close_button.set_can_focus(False)
        self.close_button.get_style_context().add_class("top_bar_button")

        # Main container holding everything
        self.box = Gtk.Box()
        self.box.pack_start(self.prev_button, False, False, 0)
        self.box.pack_start(self.next_button, False, False, 0)
        self.box.pack_start(self.align_header, False, False, 0)
        self.box.pack_end(self.close_button, False, False, 0)
        self.box.set_size_request(window_width, 44)

        self.add(self.box)

        attach_cursor_events(self.prev_button)
        attach_cursor_events(self.next_button)
        attach_cursor_events(self.close_button)
        # On start, disable the prev and next buttons
        self.disable_prev()
        self.disable_next()

    def disable_prev(self):
        self.prev_button.set_sensitive(False)
        self.prev_button.set_image(self.pale_prev_arrow)

    def enable_prev(self):
        self.prev_button.set_sensitive(True)
        self.prev_button.set_image(self.dark_prev_arrow)

    def disable_next(self):
        self.next_button.set_sensitive(False)
        self.next_button.set_image(self.pale_next_arrow)

    def enable_next(self):
        self.next_button.set_sensitive(True)
        self.next_button.set_image(self.dark_next_arrow)

    def set_prev_callback(self, callback):
        self.prev_button.connect("button_press_event", callback)

    def set_next_callback(self, callback):
        self.next_button.connect("button_press_event", callback)

    def set_close_callback(self, callback):
        self.close_button.connect("button_press_event", callback)
