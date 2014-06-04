
#!/usr/bin/env python

# kano_dialog.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This is a custom dialog pop up styled in Gtk 3
#
# Example usage:
# from kano.gtk3 import kano_dialog
#
# kdialog = kano_dialog.KanoDialog("title", "description", {"OK": 0,"CANCEL": -1})
# response = kdialog.run()
# if response == 0:
#   print "OK button was clicked"
# else:
#   print "CANCEL button was clicked"


from gi.repository import Gtk, Gdk
from kano.gtk3.green_button import GreenButton
from kano.gtk3.heading import Heading
from kano.paths import common_css_dir
import os


radio_returnvalue = None


class KanoDialog():
    # button_dict includes the button text and button return values
    def __init__(self, title_text="", description_text="", button_dict=None, widget=None, has_entry=False, has_list=False):
        self.title_text = title_text
        self.description_text = description_text
        self.widget = widget
        self.button_dict = button_dict
        self.returnvalue = 0
        self.launch_dialog()
        self.has_entry = has_entry

        self.has_list = has_list

    def launch_dialog(self, widget=None, event=None):

        cssProvider = Gtk.CssProvider()
        path = os.path.join(common_css_dir, "dialog.css")
        cssProvider.load_from_path(path)
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.dialog = Gtk.Dialog()
        self.dialog.set_decorated(False)
        self.dialog.set_resizable(False)
        self.dialog.set_border_width(5)

        content_area = self.dialog.get_content_area()
        background = Gtk.EventBox()
        background.get_style_context().add_class("white")
        content_area.reparent(background)
        self.dialog.add(background)
        self.title = Heading(self.title_text, self.description_text)
        content_area.pack_start(self.title.container, False, False, 0)
        self.buttons = []
        button_box = Gtk.Box()

        if self.button_dict is None or self.button_dict == {}:
            button_name = "OK"
            return_value = 0
            self.button_dict = {button_name: return_value}

        for button_name, return_value in self.button_dict.iteritems():
            button = GreenButton(button_name)
            button.connect("button-press-event", self.exit_dialog, return_value)
            self.buttons.append(button)
            button_box.pack_end(button, False, False, 10)

        alignment = Gtk.Alignment(xscale=0, yscale=1, xalign=0.5, yalign=1)
        alignment.add(button_box)

        if self.widget is not None:
            content_area.pack_start(self.widget, False, False, 0)

        content_area.pack_start(alignment, False, False, 10)

    def exit_dialog(self, widget, event, return_value):
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            self.returnvalue = return_value
            # TODO: improve this logic
            if self.has_entry:
                self.returnvalue = self.widget.get_text()
            elif self.has_list:
                # get selected radio button
                self.returnvalue = radio_returnvalue
            self.dialog.destroy()
            return self.returnvalue

    def run(self):
        self.dialog.show_all()
        self.dialog.run()
        return self.returnvalue

    def set_text(self, title_text, description_text):
        self.title_text = title_text
        self.description_text = description_text
        self.title.set_text(title_text, description_text)
