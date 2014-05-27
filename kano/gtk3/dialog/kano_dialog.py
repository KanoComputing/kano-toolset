
#!/usr/bin/env python

# kano_dialog.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This is a custom dialog pop up styled in Gtk 3


from gi.repository import Gtk, Gdk
import os


class KanoDialog():
    # button_dict includes the button text and button return values
    def __init__(self, title_text="", heading_text="", button_dict=None, widget=None):
        self.title_text = title_text
        self.heading_text = heading_text
        self.widget = widget
        self.button_dict = button_dict
        self.returnvalue = 0
        self.launch_dialog()

    def launch_dialog(self, widget=None, event=None):
        self.dialog = Gtk.Dialog()
        self.dialog.set_decorated(False)
        self.dialog.set_size_request(300, 100)
        self.dialog.set_resizable(False)
        self.dialog.set_border_width(5)

        content_area = self.dialog.get_content_area()
        background = Gtk.EventBox()
        background.get_style_context().add_class("white")
        content_area.reparent(background)
        self.dialog.add(background)
        self.title = Heading(self.title_text, self.heading_text)
        content_area.pack_start(self.title.container, False, False, 0)
        self.buttons = []
        button_box = Gtk.Box()

        if self.button_dict is None:
            button_name = "OK"
            return_value = 0
            self.button_dict = {button_name: return_value}

        for button_name, return_value in self.button_dict.iteritems():
            button = Gtk.Button(button_name)
            button.connect('button-press-event', self.exit_dialog, return_value)
            button.connect('key-press-event', self.exit_dialog, return_value)
            button.get_style_context().add_class("green_button")
            attach_cursor_events(button)
            self.buttons.append(button)
            button_box.pack_end(button, False, False, 10)

        alignment = Gtk.Alignment(xscale=0, yscale=1, xalign=0.5, yalign=1)
        alignment.add(button_box)

        if self.widget is not None:
            content_area.pack_start(self.widget, False, False, 0)

        content_area.pack_start(alignment, False, False, 10)

    def exit_dialog(self, widget, event, return_value):
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            self.dialog.destroy()
            arrow_cursor(self.dialog, None)
            self.returnvalue = return_value
            return return_value

    def run(self):
        self.dialog.show_all()
        self.dialog.run()
        return self.returnvalue

    def set_text(self, title_text, heading_text):
        self.title_text = title_text
        self.heading_text = heading_text
        self.title.set_text(title_text, heading_text)


class Heading():
    def __init__(self, title, description):

        self.title = Gtk.Label(title)
        self.description = Gtk.Label(description)

        self.title_style = self.title.get_style_context()
        self.title_style.add_class('title')

        self.description_style = self.description.get_style_context()
        self.description_style.add_class('description')

        # Table
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.container.pack_start(self.title, False, False, 6)
        self.container.pack_start(self.description, False, False, 0)

    def set_text(self, title, description):
        self.title.set_text(title)
        self.description.set_text(description)

    def get_text(self):
        return [self.title.get_text(), self.description.get_text()]


# cursor functions
def hand_cursor(button, event):
    # Change the cursor to hand
    cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
    button.get_root_window().set_cursor(cursor)


def arrow_cursor(button, event):
    # Set the cursor to normal Arrow
    cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
    button.get_root_window().set_cursor(cursor)


def get_path():
    # setting up directories
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # local path
    styles_local = os.path.join(dir_path, 'styles/dialog.css')
    # bin path
    styles_usr = '/usr/lib/python2.7/dist-packages/styles/dialog.css'
    if os.path.exists(styles_local):
        styles_dir = styles_local
        return styles_dir
    elif os.path.exists(styles_usr):
        styles_dir = styles_usr
        return styles_dir
    else:
        raise Exception('Neither local nor usr styles found!')


def attach_cursor_events(button):
    button.connect('enter-notify-event', hand_cursor)
    button.connect('leave-notify-event', arrow_cursor)
    button.connect('button-press-event', arrow_cursor)


# TEST DIALOG
if __name__ == '__main__':
    KanoDialog("Here is a test dialog", "What do you think?")
