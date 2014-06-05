
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
from kano.gtk3.buttons import KanoButton
from kano.gtk3.heading import Heading
from kano.paths import common_css_dir
import os


radio_returnvalue = None
button_defaults = {'return_value': 0, 'color': 'green'}
background_colors = ['grey', 'white']


class KanoDialog():
    # button_dict includes the button text, color and button return values
    def __init__(self, title_text="", description_text="", button_dict=None, widget=None, has_entry=False, has_list=False):
        self.title_text = title_text
        self.description_text = description_text
        self.widget = widget
        self.button_dict = button_dict
        self.returnvalue = 0
        self.has_entry = has_entry
        self.has_list = has_list

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
        self.content_background = Gtk.EventBox()
        self.content_background.get_style_context().add_class("white")
        self.content_background.set_size_request(140, 140)
        content_area.reparent(self.content_background)
        action_area = self.dialog.get_action_area()
        self.action_background = Gtk.EventBox()
        self.action_background.get_style_context().add_class("white")
        action_area.reparent(self.action_background)
        action_area.set_layout(Gtk.ButtonBoxStyle.CENTER)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.add(self.content_background)
        container.add(self.action_background)
        self.dialog.add(container)

        self.title = Heading(self.title_text, self.description_text)
        content_area.pack_start(self.title.container, False, False, 0)
        self.buttons = []
        button_box = Gtk.Box()

        if self.button_dict is None or self.button_dict == {}:
            self.button_dict = {"OK": button_defaults}

        # Replace the empty arguments with the defaults
        for button_name, button_arguments in self.button_dict.iteritems():
            for argument, value in button_defaults.iteritems():
                if not argument in button_arguments:
                    button_arguments[argument] = value

            color = button_arguments['color']
            return_value = button_arguments['return_value']

            button = KanoButton(button_name)
            button.set_color(color)
            button.connect("button-press-event", self.exit_dialog, return_value)
            self.buttons.append(button)
            button_box.pack_start(button, False, False, 6)

        alignment = Gtk.Alignment()
        alignment.add(button_box)
        # annoying uneven alignment - cannot seem to centre y position
        alignment.set_padding(6, 3, 0, 0)

        if self.widget is not None:
            content_area.pack_start(self.widget, False, False, 0)

        action_area.pack_start(alignment, False, False, 0)

    def exit_dialog(self, widget, event, return_value):
        # 65293 is the ENTER keycode
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

    def set_action_background(self, color):
        for c in background_colors:
            self.action_background.get_style_context().add_class(c)
        self.action_background.get_style_context().add_class(color)

