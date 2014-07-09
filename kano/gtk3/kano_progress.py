#!/usr/bin/env python

# kano_progress.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Customised progress bar widget

from gi.repository import Gtk, GObject
from kano.gtk3.apply_styles import apply_styles, apply_named_style
#import sys


class Progress(Gtk.ProgressBar):

    def __init__(self, pulse=True):

        Gtk.ProgressBar.__init__(self)
        self.activity_mode = pulse
        self.keep_going = True

        if self.activity_mode:
            self.pulse()
        else:
            self.set_fraction(0.0)

        GObject.timeout_add(50, self.on_timeout, None)

    def on_timeout(self, user_data):
        if self.activity_mode:
            self.pulse()
        else:
            new_value = self.get_fraction() + 0.01

            if new_value > 1:
                new_value = 0
                Gtk.main_quit()

            self.set_fraction(new_value)

        # As this is a timeout function, return True so that it
        # continues to get called
        return self.keep_going


class KanoProgress(Gtk.Window):

    def __init__(self, pulse, title=""):
        apply_styles()
        apply_named_style('kano_progress')

        Gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)

        label = Gtk.Label(title)
        progress = Progress(pulse)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)
        box.pack_start(label, False, False, 5)
        box.pack_start(progress, False, False, 0)




