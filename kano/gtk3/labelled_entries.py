#!/usr/bin/env python

# labelled_entries.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Template for creating a list of labelled entries

from gi.repository import Gtk


class LabelledEntries(Gtk.Alignment):

    def __init__(self, entries_info):
        Gtk.Alignment.__init__(self)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.entries = []

        # entries_info = [{"heading": "", "subheading": ""}, {"heading": "", "subheading": ""}]
        for info in entries_info:
            entry = Gtk.Entry()
            align = create_labelled_widget(info["heading"], info["subheading"], entry)
            self.entries.append(entry)
            self.box.pack_start(align, False, False, 5)

        self.add(self.box)

    def get_entries(self):
        return self.entries

    def get_entry(self, number):
        return self.entries[number]

    def get_entry_text(self):
        all_text = []

        for entry in self.entries:
            text = entry.get_text()
            all_text.append(text)

        return all_text

    def set_spacing(self, number):
        self.box.set_spacing(number)


def add_heading(text, widget, bold=False):

    label = Gtk.Label(text)
    label_alignment = Gtk.Alignment(xscale=0, xalign=0)
    label_alignment.add(label)

    if bold:
        label.get_style_context().add_class("bold_label")
    else:
        label.get_style_context().add_class("desc_label")

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.pack_start(label_alignment, False, False, 3)
    box.pack_start(widget, False, False, 3)

    return box


def create_custom_label(heading, description=""):

    heading_label = Gtk.Label(heading)
    heading_label.get_style_context().add_class("bold_label")
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.pack_start(heading_label, False, False, 0)

    if description:
        description_label = Gtk.Label(description)
        description_label.get_style_context().add_class("desc_label")
        box.pack_start(description_label, False, False, 0)

    align = Gtk.Alignment(yscale=0, yalign=0.5)
    align.add(box)

    return align


def create_labelled_widget(heading, description="", widget=None):

    label_box = create_custom_label(heading, description)
    box = Gtk.Box()
    box.pack_start(label_box, False, False, 5)
    box.pack_start(widget, False, False, 5)

    align = Gtk.Alignment(xscale=0, xalign=1)
    align.add(box)

    return align


