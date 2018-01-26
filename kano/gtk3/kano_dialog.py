
#!/usr/bin/env python

# kano_dialog.py
#
# Copyright (C) 2014 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This is a custom dialog pop up styled in Gtk 3
#
# Example usage:
# from kano.gtk3 import kano_dialog
#
# kdialog = kano_dialog.KanoDialog("title", "description", [{"label":"OK", "return_value": 0, "color": "orange"}, {"label": "CANCEL", "return_value": -1, "color": "red"}])
# response = kdialog.run()
# if response == 0:
#   print "OK button was clicked"
# else:
#   print "CANCEL button was clicked"


from gi.repository import Gtk
from kano.gtk3.buttons import KanoButton, OrangeButton
from kano.gtk3.heading import Heading
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.apply_styles import apply_common_to_screen, apply_styling_to_widget, apply_colours_to_widget
from kano.paths import common_css_dir
import os

radio_returnvalue = None
button_defaults = {'return_value': 0, 'color': 'green'}
background_colors = ['grey', 'white']


class KanoDialog():
    CSS_PATH = os.path.join(common_css_dir, "dialog.css")

    # button_dict includes the button text, color and button return values
    # It can either be a dictionary for backwards compatibility, or a list
    def __init__(self, title_text="", description_text="", button_dict=None, widget=None,
                 has_entry=False, has_list=False, scrolled_text="", global_style="", parent_window=None,
                 orange_info=None, hide_from_taskbar=False):

        self.title_text = title_text
        self.description_text = description_text
        self.widget = widget
        self.button_info = button_dict
        self.returnvalue = 0
        self.has_entry = has_entry
        self.has_list = has_list
        self.scrolled_text = scrolled_text
        self.global_style = global_style
        self.parent_window = parent_window
        self.orange_info = orange_info

        self.dialog = Gtk.Dialog()
        self.dialog.set_decorated(False)
        self.dialog.set_resizable(False)

        # TODO: review this - should this always be set?
        # self.dialog.set_keep_above(True)
        self.dialog.set_skip_taskbar_hint(hide_from_taskbar)
        self.dialog.set_border_width(5)

        apply_styling_to_widget(self.dialog, self.CSS_PATH)
        apply_colours_to_widget(self.dialog)

        # if widget or an orange button is added, to get styling correct
        # the global_styling property should be on.
        # TODO: is this needed any more?
        if global_style or (widget is not None or orange_info is not None):
            apply_common_to_screen()

        content_area, action_area = self.__colour_dialog_background()

        self.title = Heading(self.title_text, self.description_text)
        content_area.pack_start(self.title.container, False, False, 0)

        # If button_info is None, or an empty dictionary or list, default to an OK button
        if not self.button_info:
            button_defaults['label'] = _("OK")
            self.button_info = [button_defaults]

        # convert button dictionary to list
        if isinstance(self.button_info, dict):
            self.__convert_dict_to_list()

        kano_button_box = self.__generate_buttons()

        if orange_info is not None:
            button_container = self.__add_orange_button(orange_info, kano_button_box)
        else:
            button_container = Gtk.Alignment()
            button_container.add(kano_button_box)
            # annoying uneven alignment - cannot seem to centre y position
            button_container.set_padding(6, 3, 0, 0)

        action_area.pack_start(button_container, False, False, 0)

        # Add scrolled window
        if self.scrolled_text:
            scrolledwindow = self.__add_scrolled_window()
            content_area.pack_start(scrolledwindow, False, False, 0)

        # or add widget
        elif self.widget is not None:
            content_area.pack_start(self.widget, False, False, 0)

        # Set keyboard focus on first button if no entry
        if not has_entry:
            self.buttons[0].grab_focus()

        # Brings the focus back to the default button (OK) "hacky"
        if isinstance(self.widget, Gtk.Entry):
            def entry_activated(w):
                self.returnvalue = self.widget.get_text()
                self.dialog.response(Gtk.ResponseType.OK)
            self.widget.connect('activate', entry_activated)

    def __add_scrolled_window(self):
        text = Gtk.TextView()
        text.get_buffer().set_text(self.scrolled_text)
        text.set_wrap_mode(Gtk.WrapMode.WORD)
        text.set_editable(False)

        scrolledwindow = ScrolledWindow()
        scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.add_with_viewport(text)
        scrolledwindow.set_size_request(400, 200)
        scrolledwindow.apply_styling_to_widget(wide=False)

        return scrolledwindow

    def __add_orange_button(self, orange_info, kano_button_box):
        orange_text = orange_info['name']
        orange_return_value = orange_info['return_value']

        button_container = Gtk.ButtonBox(spacing=10)
        button_container.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        self.orange_button = OrangeButton(orange_text)
        self.orange_button.connect('button-release-event', self.exit_dialog, orange_return_value)

        button_container.pack_start(self.orange_button, False, False, 0)
        button_container.pack_start(kano_button_box, False, False, 0)
        # The empty label is to centre the kano_button
        label = Gtk.Label("    ")
        button_container.pack_start(label, False, False, 0)

        return button_container

    def __colour_dialog_background(self):
        content_area = self.dialog.get_content_area()
        self.content_background = Gtk.EventBox()
        self.add_style(self.content_background, 'white')
        self.content_background.set_size_request(140, 140)
        content_area.reparent(self.content_background)
        action_area = self.dialog.get_action_area()
        self.action_background = Gtk.EventBox()
        self.add_style(self.action_background, 'white')
        action_area.reparent(self.action_background)
        action_area.set_layout(Gtk.ButtonBoxStyle.CENTER)

        # Set area around the buttons grey by default
        self.set_action_background('grey')

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.add(self.content_background)
        container.add(self.action_background)
        self.dialog.add(container)

        return content_area, action_area

    def __convert_dict_to_list(self):
        button_list = []

        for button_name, button_arguments in self.button_info.iteritems():
            button_arguments['label'] = button_name
            button_list.append(button_arguments)

        self.button_info = button_list

    def __generate_buttons(self):
        self.buttons = []
        kano_button_box = Gtk.Box()

        for button in self.button_info:
            for argument, value in button_defaults.iteritems():

                # Use default info if not provided
                if argument not in button:
                    button[argument] = value

                    # Create default return values for OK and CANCEL buttons
                    if argument == 'return_value':
                        if hasattr(button, 'label'):
                            if button['label'] == _("OK"):
                                button['return_value'] = 0
                            elif button['label'] == _("CANCEL"):
                                button['return_value'] = 1
                    if argument == 'color':
                        if button['label'] == _("CANCEL"):
                            button['color'] = 'red'

            color = button['color']
            return_value = button['return_value']
            button_name = button['label']

            button = KanoButton(button_name)
            button.set_color(color)
            button.connect('button-release-event', self.exit_dialog, return_value)
            button.connect('key-release-event', self.exit_dialog, return_value)
            self.buttons.append(button)
            kano_button_box.pack_start(button, False, False, 6)

        return kano_button_box

    def add_style(self, widget, app_class):
        apply_styling_to_widget(widget, self.CSS_PATH)
        style = widget.get_style_context()
        style.add_class(app_class)

    def exit_dialog(self, button, event, return_value):
        # 65293 is the ENTER keycode
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            self.returnvalue = return_value
            # If we have an entry
            if self.has_entry:
                # We have to click an OK button to get entry value
                # May want to change this logic later to be more flexible
                if unicode(button.get_label().decode('utf8')) == _("OK"):
                    self.returnvalue = self.widget.get_text()
            elif self.has_list:
                # get selected radio button only if press the OK button
                if unicode(button.get_label().decode('utf8')) == _("OK"):
                    self.returnvalue = radio_returnvalue
            # TODO: change the structure so we emit different signals depending on the button clicked
            self.dialog.response(Gtk.ResponseType.OK)

        # Indicate that the signal has been handled
        return True

    def run(self):
        if self.parent_window is not None:
            # Make the dialog always above the parent window
            self.dialog.set_transient_for(self.parent_window)

        if self.parent_window is not None and \
           hasattr(self.parent_window, 'blur') and \
           callable(self.parent_window.blur):
            self.parent_window.blur()

        self.dialog.show_all()
        self.dialog.set_icon_name('kano-dialog')
        self.dialog.run()
        self.dialog.destroy()

        if self.parent_window is not None and \
           hasattr(self.parent_window, 'unblur') and \
           callable(self.parent_window.unblur):
            self.parent_window.unblur()

        return self.returnvalue

    def close(self):
        '''
        Use this method if your app is nesting several Kano Dialogs,
        and you need to step through without stacking them up.
        '''
        self.dialog.destroy()

        # Dispatch events so Gtk has a chance to close the dialog
        while Gtk.events_pending():
            Gtk.main_iteration()

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
    global_style = False
    hide_from_taskbar = False

    for arg in args:
        split = arg.split('=')

        if split[0] == 'button':
            button_options = {}
            button_values = split[1].split(',')
            button_name = button_values[0]
            buttons[button_name] = button_options
            for name, default in button_defaults.iteritems():
                for value in button_values:
                    if name in value:
                        pair = value.split(':')
                        button_options[pair[0]] = pair[1]

        if split[0] == 'buttons':
            buttons_arg = split[1].split(',')
            for button_arg in buttons_arg:
                name, color, rc = button_arg.split(':')
                buttons[name] = {
                    'color': color,
                    'return_value': int(rc),
                }

        if split[0] == 'radiolist':
            widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            has_list = True
            radio_list = split[1].split(',')
            radio = Gtk.RadioButton.new_with_label_from_widget(None, radio_list[0])
            radio.connect('toggled', on_button_toggled)
            radio_returnvalue = radio_list[0]
            widget.pack_start(radio, False, False, 5)
            for i in radio_list[1:]:
                r = Gtk.RadioButton.new_with_label_from_widget(radio, i)
                r.connect('toggled', on_button_toggled)
                widget.pack_start(r, False, False, 5)

        elif split[0] == 'entry':
            widget = Gtk.Entry()
            has_entry = True
            if len(split) == 2 and split[1] == 'hidden':
                widget.set_visibility(False)

        if split[0] == 'title':
            title = split[1]

        if split[0] == 'description':
            description = split[1]

        if split[0] == 'scrolled_text':
            scrolled_text = split[1]

        if split[0] == 'global_style':
            global_style = True

        if split[0] == 'no-taskbar':
            hide_from_taskbar = True

    return title, description, buttons, widget, has_entry, has_list, scrolled_text, global_style, hide_from_taskbar


def on_button_toggled(button):
    global radio_returnvalue

    if button.get_active():
        label = button.get_label()
        radio_returnvalue = label
