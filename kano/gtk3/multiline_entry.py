#
# multiline_entry.py
#
# Copyright (C) 2015 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Modified Gtk.TextView to permit placeholder text and other functions to make
# it more consistent with GtkEntry
#

import os

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk, GObject

from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.apply_styles import apply_styling_to_screen

from kano.paths import common_css_dir


class KanoTextBuffer(Gtk.TextBuffer):
    __gsignals__ = {
        'insert-text': 'override'
    }

    def __init__(self):
        Gtk.TextBuffer.__init__(self)
        self._max_length = 0

    @property
    def max_length(self):
        return self._max_length

    @max_length.setter
    def max_length(self, value):
        self._max_length = max(value, 0)

    def get_max_length(self):
        """ Same as self.max_length
        It is provided to be consistent with the Gtk paradigm
        """
        return self.max_length

    def set_max_length(self, length):
        """ Same as self.max_length = length.
        It is provided to be consistent with the Gtk paradigm
        """
        self.max_length = length

    def do_insert_text(self, location, text, length):
        max_length = self.max_length
        buffer_char_count = self.get_char_count()

        if max_length > 0 and (buffer_char_count + length) > max_length:
            new_length = max_length - buffer_char_count
            new_text = text[:new_length]
        else:
            new_length = length
            new_text = text
        Gtk.TextBuffer.do_insert_text(
            self, location, new_text, new_length
        )
        return False


class MultilineEntry(Gtk.EventBox):
    __gsignals__ = {
        'changed': (GObject.SIGNAL_RUN_LAST, None, (KanoTextBuffer,)),
    }

    def __init__(self, border_width=2):
        Gtk.EventBox.__init__(self)

        # Very hacky way to get a border (gg GTK): create a grey event box
        # which is a little bigger than the white event box containing the
        # widget
        apply_styling_to_screen(
            os.path.join(common_css_dir, 'multiline_entry.css')
        )
        self.get_style_context().add_class('gray-box')
        widget_box = Gtk.EventBox()
        widget_box.get_style_context().add_class('white-box')
        widget_box.set_margin_left(border_width)    # gray border width (px)
        widget_box.set_margin_right(border_width)
        widget_box.set_margin_top(border_width)
        widget_box.set_margin_bottom(border_width)
        self.add(widget_box)

        # putting the TextView into a ScrolledWindow so it doesn't resize
        # horiz & vert
        scrolled_window = ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        scrolled_window.apply_styling_to_widget()
        widget_box.add(scrolled_window)

        # creating the actual TextView
        self.text_view = Gtk.TextView()
        # break on words, then chars
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        # the white border inside the thin gray border
        self.text_view.set_margin_left(10)
        self.text_view.set_margin_right(10)
        self.text_view.set_margin_top(10)
        self.text_view.set_margin_bottom(10)
        scrolled_window.add(self.text_view)

        # placeholder text logic
        self.placeholder_text = None
        self.placeholder_text_set = False
        self.restore_buffer_handler_id = None
        self.clear_buffer_handler_id = None

        self.text_view.set_buffer(KanoTextBuffer())
        text_buffer = self.text_view.get_buffer()
        text_buffer.connect('changed', self._on_changed)

    def get_text(self):
        if self.placeholder_text_set:
            return ''

        textbuffer = self.text_view.get_buffer()
        start = textbuffer.get_start_iter()
        end = textbuffer.get_end_iter()

        return textbuffer.get_text(start, end, False)

    def set_placeholder_text(self, text):
        self.placeholder_text = text
        self._restore_placeholder_text()

    def _on_changed(self, text_buffer):
        self.emit('changed', text_buffer)

    def _restore_placeholder_text(self, *dummy_args, **dummy_kwargs):
        text = self.get_text()

        if not text:
            self.placeholder_text_set = True

            if self.restore_buffer_handler_id:
                self.disconnect(self.restore_buffer_handler_id)

            self.set_text(self.placeholder_text)

            self.clear_buffer_handler_id = self.text_view.connect(
                'focus-in-event', self._clear_buffer
            )
            self.text_view.get_style_context().remove_class('entry-text')
            self.text_view.get_style_context().add_class('placeholder-text')

    def set_text(self, text):
        textbuffer = self.text_view.get_buffer()
        textbuffer.set_text(text)

    def set_max_length(self, max_length):
        self.text_view.get_buffer().set_max_length(max_length)

    def get_max_length(self, max_length):
        return self.text_view.get_buffer().max_length

    def _clear_buffer(self, *dummy_args, **dummy_kwargs):
        text = self.get_text()

        if not text:
            self.placeholder_text_set = False
            self.text_view.get_style_context().remove_class('placeholder-text')
            self.text_view.get_style_context().add_class('entry-text')

            textbuffer = self.text_view.get_buffer()
            start = textbuffer.get_start_iter()
            end = textbuffer.get_end_iter()
            textbuffer.delete(start, end)

            if self.clear_buffer_handler_id:
                self.text_view.disconnect(self.clear_buffer_handler_id)

            self.restore_buffer_handler_id = self.text_view.connect(
                'focus-out-event', self._restore_placeholder_text
            )
