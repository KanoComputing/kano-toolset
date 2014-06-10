#!/usr/bin/env python

# top_bar.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the (pretend) top window bar.

from gi.repository import Gtk
from kano.gtk3 import icons
from kano.gtk3.cursor import attach_cursor_events
from kano.paths import common_css_dir
import os
import sys

TOP_BAR_HEIGHT = 44
HEADER_WIDTH = 100


class TopBar(Gtk.EventBox):
    def __init__(self, title, window_width=-1, has_buttons=True):

        Gtk.EventBox.__init__(self)

        space_taken = 0
        self.has_buttons = has_buttons
        if has_buttons:
            space_taken = 44 * 4

        # Styling
        self.cssProvider = Gtk.CssProvider()
        top_bar_css = os.path.join(common_css_dir, 'top_bar.css')
        if not os.path.exists(top_bar_css):
            sys.exit('CSS file missing!')
        self.cssProvider.load_from_path(top_bar_css)
        styleContext = self.get_style_context()
        styleContext.add_provider(self.cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.set_size_request(window_width, TOP_BAR_HEIGHT)

        self.height = TOP_BAR_HEIGHT

        self.header = Gtk.Label(title, halign=Gtk.Align.CENTER)
        self.header.set_size_request(HEADER_WIDTH, TOP_BAR_HEIGHT)

        if window_width == -1:
            self.align_header = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1, yscale=1)
        else:
            self.align_header = Gtk.Alignment(xalign=0, yalign=0.5, xscale=0, yscale=0)
            padding_left = (window_width - space_taken - HEADER_WIDTH) / 2
            self.align_header.set_padding(0, 0, padding_left, 0)

        self.align_header.add(self.header)

        self.cross = icons.set_from_name("cross")

        # Close button
        self.close_button = Gtk.Button()
        self.close_button.set_image(self.cross)
        self.close_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        self.close_button.set_can_focus(False)
        self.add_style(self.close_button, "top_bar_button")

        # Main container holding everything
        self.box = Gtk.Box()

        if has_buttons:

            # Icons of the buttons
            self.pale_prev_arrow = icons.set_from_name("pale_left_arrow")
            self.pale_next_arrow = icons.set_from_name("pale_right_arrow")
            self.dark_prev_arrow = icons.set_from_name("dark_left_arrow")
            self.dark_next_arrow = icons.set_from_name("dark_right_arrow")

            # Prev Button
            self.prev_button = Gtk.Button()
            self.prev_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
            self.prev_button.set_can_focus(False)
            self.prev_button.set_image(self.pale_prev_arrow)

            # Next button
            self.next_button = Gtk.Button()
            self.next_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
            self.next_button.set_can_focus(False)
            self.next_button.set_image(self.pale_next_arrow)

            self.box.pack_start(self.prev_button, False, False, 0)
            self.box.pack_start(self.next_button, False, False, 0)

            self.add_style(self.prev_button, "top_bar_button")
            self.add_style(self.next_button, "top_bar_button")

            # On start, disable the prev and next buttons
            self.disable_prev()
            self.disable_next()

            attach_cursor_events(self.prev_button)
            attach_cursor_events(self.next_button)

        attach_cursor_events(self.close_button)

        self.box.pack_start(self.align_header, False, False, 0)
        self.box.pack_end(self.close_button, False, False, 0)
        self.box.set_size_request(window_width, 44)

        self.add(self.box)

        styleContext.add_class('top_bar_container')
        self.add_style(self.header, "top_bar_title")

    def add_style(self, widget, app_class):
        style = widget.get_style_context()
        style.add_provider(self.cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style.add_class(app_class)

    def disable_prev(self):
        if self.has_buttons:
            self.prev_button.set_sensitive(False)
            self.prev_button.set_image(self.pale_prev_arrow)

    def enable_prev(self):
        if self.has_buttons:
            self.prev_button.set_sensitive(True)
            self.prev_button.set_image(self.dark_prev_arrow)

    def disable_next(self):
        if self.has_buttons:
            self.next_button.set_sensitive(False)
            self.next_button.set_image(self.pale_next_arrow)

    def enable_next(self):
        if self.has_buttons:
            self.next_button.set_sensitive(True)
            self.next_button.set_image(self.dark_next_arrow)

    def set_prev_callback(self, callback):
        if self.has_buttons:
            self.prev_button.connect("button_press_event", callback)

    def set_next_callback(self, callback):
        if self.has_buttons:
            self.next_button.connect("button_press_event", callback)

    def set_close_callback(self, callback):
        self.close_button.connect("button_press_event", callback)
