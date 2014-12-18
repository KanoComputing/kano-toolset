#!/usr/bin/env python

# kano_progress.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Customised progress bar widget

import os
import sys
from gi.repository import Gtk, GObject

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano.gtk3.apply_styles import apply_colours_to_screen, apply_styling_to_screen
from kano.paths import common_css_dir

# Be careful you don't call another function with this
GObject.threads_init()
import threading
import time


class ProgressBar(Gtk.ProgressBar):
    def __init__(self, pulse=True, rate=0.01):

        Gtk.ProgressBar.__init__(self)
        self.activity_mode = pulse
        self.still_working = True
        self.progress_rate = rate

        if self.activity_mode:
            self.pulse()
        else:
            self.set_fraction(0.0)

        GObject.timeout_add(50, self.on_timeout, None)

    def on_timeout(self, user_data):
        if self.activity_mode:
            self.pulse()
        else:
            new_value = self.get_fraction() + self.progress_rate
            if new_value > 1:
                new_value = 0
                self.win.close()

            self.set_fraction(new_value)

        if not self.still_working:
            self.win.close()

        # As this is a timeout function, return True so that it
        # continues to get called
        return self.still_working

    def work(self):  # This would be the actual time-consuming workload
        if hasattr(self, "work_function"):

            if hasattr(self, "work_args"):
                self.work_function(self.work_args)
            else:
                self.work_function()

    def set_work_function(self, function, args=None):
        self.work_function = function
        if args is not None:
            self.work_args = args


class KanoProgressBar(ProgressBar):
    CSS_PATH = os.path.join(common_css_dir, 'kano_progress.css')

    def __init__(self, pulse=True, title="", rate=0.01):
        apply_colours_to_screen()
        apply_styling_to_screen(self.CSS_PATH)

        ProgressBar.__init__(self, pulse, rate)
        self.get_style_context().add_class("KanoProgressBar")

        self.win = Gtk.Window()
        self.win.get_style_context().add_class("KanoProgressBar")
        self.win.set_decorated(False)
        self.win.set_resizable(False)
        self.win.set_position(Gtk.WindowPosition.CENTER)
        self.win.connect("delete-event", Gtk.main_quit)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.win.add(box)

        label = Gtk.Label(title)
        label.set_padding(10, 10)
        label.get_style_context().add_class("KanoProgressBar")
        box.pack_start(label, False, False, 5)
        box.pack_start(self, False, False, 0)

    def run(self):
        self.win.show_all()
        # Thread running the long process
        if self.activity_mode:
            wt = WorkerThread(self.work, self)
            wt.start()
        Gtk.main()


class WorkerThread(threading.Thread):
    def __init__(self, function, parent):
        threading.Thread.__init__(self)
        self.function = function
        self.parent = parent

    def run(self):
        self.parent.still_working = True
        self.function()
        # This is here to make the GUI progress stop and quit
        self.parent.still_working = False


if __name__ == "__main__":
    pb = KanoProgressBar(title="Here is a title")
    pb.set_work_function(time.sleep, 2)
    pb.run()
