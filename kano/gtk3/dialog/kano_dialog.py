
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

    def __init__(self, title_text="", heading_text="", callback=None, widget=None):
        self.title_text = title_text
        self.heading_text = heading_text
        self.callback = callback
        self.widget = widget
        self.launch_dialog()

    def launch_dialog(self, widget=None, event=None):

        cssProvider = Gtk.CssProvider()
        dir_path = get_path()
        cssProvider.load_from_path(dir_path)
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

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
        self.dialog_button = Gtk.Button("EXIT")
        self.dialog_button.get_style_context().add_class("green_button")
        attach_cursor_events(self.dialog_button)
        self.dialog_button.connect("button_press_event", self.exit_dialog)
        self.dialog_button.connect('key-press-event', self.exit_dialog)

        button_box = Gtk.Box()
        button_box.add(self.dialog_button)
        alignment = Gtk.Alignment(xscale=0, yscale=1, xalign=0.5, yalign=1)
        alignment.add(button_box)

        if self.widget is not None:
            content_area.pack_start(self.widget, False, False, 0)

        content_area.pack_start(alignment, False, False, 10)
        self.dialog.show_all()
        self.dialog.run()

    def exit_dialog(self, widget, event):
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            self.dialog.destroy()
            arrow_cursor(self.dialog, None)
            if self.callback is not None:
                self.callback()

    def set_callback(self, callback):
        self.callback = callback
        self.dialog_button.connect("button_press_event", self.exit_dialog)

    def set_text(self, title_text, heading_text):
        self.title_text = title_text
        self.heading_text = heading_text
        self.title.set_text(title_text, heading_text)

    def set_button_text(self, text):
        self.dialog_button.set_label(text)


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
