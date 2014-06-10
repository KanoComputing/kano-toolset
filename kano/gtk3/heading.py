
#!/usr/bin/env python

# kano_dialog.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Heading used frequently around kano-settings and kano-login

from gi.repository import Gtk
from kano.paths import common_css_dir


class Heading():
    def __init__(self, title, description):

        self.title = Gtk.Label(title)
        self.description = Gtk.Label(description)

        # Table
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.container.pack_start(self.title, False, False, 6)
        self.container.pack_start(self.description, False, False, 0)

        cssProvider = Gtk.CssProvider()
        cssProvider.load_from_path(common_css_dir + "/heading.css")
        styleContext = Gtk.StyleContext()
        styleContext.add_provider(cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.title_style = self.title.get_style_context()
        self.title_style.add_provider(cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.title_style.add_class('title')

        self.description_style = self.description.get_style_context()
        self.description_style.add_provider(cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.description_style.add_class('description')

    def set_text(self, title, description):
        self.title.set_text(title)
        self.description.set_text(description)

    def get_text(self):
        return [self.title.get_text(), self.description.get_text()]
