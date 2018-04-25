#
# blur_overlay.py
#
# Copyright (C) 2016 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# An overlay to add blur effect
#

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk

from kano.gtk3.buttons import KanoButton
from kano.gtk3.apply_styles import apply_styling_to_widget


class BlurOverlay(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)

        self._loading = False

        self._blur = Gtk.EventBox()
        self._blur.get_style_context().add_class('blur')

        self._spinner = Gtk.Spinner()
        self._spinner.props.active = True
        apply_styling_to_widget(self._spinner, KanoButton.SPINNER_CSS)

    def _add_blur(self):
        self.add_overlay(self._blur)
        self._blur.show()

    def _rm_blur(self):
        self.remove(self._blur)

    def _add_spinner(self):
        self.add_overlay(self._spinner)
        self._spinner.show()
        self._spinner.start()

    def _rm_spinner(self):
        if self._spinner in self.get_children():
            self.remove(self._spinner)

        self._spinner.stop()

    def blur(self):
        if self._loading:
            return

        self._add_blur()
        self._add_spinner()

        self._loading = True

        self.show_all()

    def unblur(self):
        if not self._loading:
            return

        self._rm_blur()
        self._rm_spinner()

        self._loading = False
