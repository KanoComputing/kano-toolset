#
# icons.py
#
# Copyright (C) 2014 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Creates pixbufs that we can use to make images from.  Uses a strip of icons,
# each 24px by 24px.
#

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf
from kano.paths import common_images_dir
import os

# To make an image using the pixbuf icon, use the command below:
# image.set_from_pixbuf(self.pixbuf)


def set_from_name(name):
    icon_number = 0
    if name == "green_arrow":
        icon_number = 0
    elif name == "pale_right_arrow":
        icon_number = 1
    elif name == "dark_left_arrow":
        icon_number = 2
    elif name == "dark_right_arrow":
        icon_number = 3
    elif name == "pale_left_arrow":
        icon_number = 4
    elif name == "tick":
        icon_number = 5
    elif name == "cross":
        icon_number = 6
    elif name == "dropdown_arrow":
        icon_number = 7
    # Create main window
    filename = os.path.join(common_images_dir, "icons.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 192, 24)
    subpixbuf = pixbuf.new_subpixbuf(24 * icon_number, 0, 24, 24).add_alpha(True, 255, 255, 255)
    image = Gtk.Image()
    image.set_from_pixbuf(subpixbuf)
    return image
