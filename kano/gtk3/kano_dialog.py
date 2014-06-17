
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
# kdialog = kano_dialog.KanoDialog("title", "description", {"OK": {"return_value": 0, "color": "orange"},"CANCEL": {"return_value": -1, "color": "red"}})
# response = kdialog.run()
# if response == 0:
#   print "OK button was clicked"
# else:
#   print "CANCEL button was clicked"


from gi.repository import Gtk
from kano.gtk3.buttons import KanoButton
from kano.gtk3.heading import Heading
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.paths import common_css_dir
import os

radio_returnvalue = None
button_defaults = {'return_value': 0, 'color': 'green'}
background_colors = ['grey', 'white']


class KanoDialog():
    # button_dict includes the button text, color and button return values
    def __init__(self, title_text="", description_text="", button_dict=None, widget=None, has_entry=False, has_list=False, scrolled_text=None):
        self.title_text = title_text
        self.description_text = description_text
        self.widget = widget
        self.button_dict = button_dict
        self.returnvalue = 0
        self.has_entry = has_entry
        self.has_list = has_list
        self.scrolled_text = scrolled_text

        self.dialog = Gtk.Dialog()

        self.dialog_provider = Gtk.CssProvider()
        dialog_path = os.path.join(common_css_dir, "dialog.css")
        self.dialog_provider.load_from_path(dialog_path)

        self.colour_provider = Gtk.CssProvider()
        colours_path = os.path.join(common_css_dir, "colours.css")
        self.colour_provider.load_from_path(colours_path)

        styleContext = self.dialog.get_style_context()
        styleContext.add_provider(self.dialog_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        styleContext.add_provider(self.colour_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.dialog.set_decorated(False)
        self.dialog.set_resizable(False)
        self.dialog.set_keep_above(True)
        self.dialog.set_border_width(5)

        content_area = self.dialog.get_content_area()
        self.content_background = Gtk.EventBox()
        self.add_style(self.content_background, "white")
        self.content_background.set_size_request(140, 140)
        content_area.reparent(self.content_background)
        action_area = self.dialog.get_action_area()
        self.action_background = Gtk.EventBox()
        self.add_style(self.action_background, "white")
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

                    # Create default return values for OK and CANCEL buttons
                    if argument == "return_value":
                        if button_name.upper() == "OK":
                            button_arguments["return_value"] = 0
                        if button_name.upper() == "CANCEL":
                            button_arguments["return_value"] = 1

            color = button_arguments['color']
            return_value = button_arguments['return_value']

            button = KanoButton(button_name)
            button.set_color(color)
            button.connect("button-press-event", self.exit_dialog, return_value)
            button.connect("key-release-event", self.exit_dialog, return_value)
            self.buttons.append(button)
            button_box.pack_start(button, False, False, 6)

        alignment = Gtk.Alignment()
        alignment.add(button_box)
        # annoying uneven alignment - cannot seem to centre y position
        alignment.set_padding(6, 3, 0, 0)

        # Add scrolled window
        if self.scrolled_text is not None:
            scrolledwindow = ScrolledWindow()
            scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

            text = Gtk.TextView()
            text.get_buffer().set_text(self.scrolled_text)
            text.set_wrap_mode(Gtk.WrapMode.WORD)
            text.set_editable(False)
            # Stop a cursor appearing in the textview
            text.set_can_focus(False)
            scrolledwindow.add_with_viewport(text)
            styleContext = text.get_style_context()
            styleContext.add_provider(self.colour_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            styleContext.add_provider(self.dialog_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

            scrolledwindow.set_size_request(400, 200)
            content_area.pack_start(scrolledwindow, False, False, 0)

        # or add widget
        elif self.widget is not None:
            content_area.pack_start(self.widget, False, False, 0)
            styleContext = self.widget.get_style_context()
            styleContext.add_provider(self.dialog_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            styleContext.add_provider(self.colour_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        action_area.pack_start(alignment, False, False, 0)

    def add_style(self, widget, app_class):
        style = widget.get_style_context()
        style.add_provider(self.dialog_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style.add_class(app_class)

    def exit_dialog(self, button, event, return_value):
        # 65293 is the ENTER keycode
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            self.returnvalue = return_value
            # If we have an entry
            if self.has_entry:
                # We have to click an OK button to get entry value
                # May want to change this logic later to be more flexible
                if return_value == 0 and button.get_label().upper() == "OK":
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


def parse_items(args):
    global radio_returnvalue

    widget = None
    title = ""
    description = ""
    scrolled_text = ""
    has_entry = False
    has_list = False
    buttons = {}

    for arg in args:
        split = arg.split('=')

        if split[0] == "button":
            button_options = {}
            button_values = split[1].split(',')
            button_name = button_values[0]
            buttons[button_name] = button_options
            for name, default in button_defaults.iteritems():
                for value in button_values:
                    if name in value:
                        pair = value.split(':')
                        button_options[pair[0]] = pair[1]

        if split[0] == "buttons":
            buttons_arg = split[1].split(',')
            for button_arg in buttons_arg:
                name, color, rc = button_arg.split(':')
                buttons[name] = {
                    'color': color,
                    'return_value': int(rc),
                }

        if split[0] == "radiolist":
            widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            has_list = True
            radio_list = split[1].split(",")
            radio = Gtk.RadioButton.new_with_label_from_widget(None, radio_list[0])
            radio.connect("toggled", on_button_toggled)
            radio_returnvalue = radio_list[0]
            widget.pack_start(radio, False, False, 5)
            for i in radio_list[1:]:
                r = Gtk.RadioButton.new_with_label_from_widget(radio, i)
                r.connect("toggled", on_button_toggled)
                widget.pack_start(r, False, False, 5)

        elif split[0] == "entry":
            widget = Gtk.Entry()
            has_entry = True
            if len(split) == 2 and split[1] == "hidden":
                widget.set_visibility(False)

        if split[0] == 'title':
            title = split[1]

        if split[0] == 'description':
            description = split[1]

        if split[0] == "scrolled_text":
            scrolled_text = split[1]

    return title, description, buttons, widget, has_entry, has_list, scrolled_text


def on_button_toggled(button):
    global radio_returnvalue

    if button.get_active():
        label = button.get_label()
        radio_returnvalue = label
