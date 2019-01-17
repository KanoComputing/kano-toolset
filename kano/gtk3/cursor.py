#
# cursor.py
#
# Copyright (C) 2014-2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Functions that changes the cursor's appearence
#

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gdk


# win is passed through as an argument
def hand_cursor(button, event):
    # Change the cursor to hand
    cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
    button.get_root_window().set_cursor(cursor)


def arrow_cursor(button, event):
    # Set the cursor to normal Arrow
    cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
    button.get_root_window().set_cursor(cursor)


def attach_cursor_events(button):
    button.connect('enter-notify-event', hand_cursor)
    button.connect('leave-notify-event', arrow_cursor)
    button.connect('button-press-event', arrow_cursor)
