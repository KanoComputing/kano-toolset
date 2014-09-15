#!/usr/bin/env python

# kano_combobox.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This is an improved ComboBox (Dropdown) widget.
# It's main advantage over the default is it's ability to set
# the number of items to display when the dropdown is poped up.


import os
import sys
import types
from gi.repository import Gtk, Gdk, GObject, GdkPixbuf


if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano.gtk3.apply_styles import apply_styles
from kano.paths import common_images_dir, common_css_dir


class KanoComboBox(Gtk.Button):

    # default size for the combobox - use set_size_request to change these
    WIDTH = 250
    HEIGHT = 100

    ARROW_DOWN = os.path.join(common_images_dir, "arrow_down.png")
    SCROLL_ARROW_UP = os.path.join(common_images_dir, "scroll_arrow_up.png")
    SCROLL_ARROW_DOWN = os.path.join(common_images_dir, "scroll_arrow_down.png")

    # signals which are emitted in addition to Button signals
    __gsignals__ = {
        "popup": (GObject.SIGNAL_RUN_FIRST, None, ()),
        # TODO? "popdown": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "selected": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "changed": (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    #
    # default_text         the initial text displayed inside the combobox
    # items                a list of string items to build the dropdown menu from
    # max_display_items    the number of items to display when poping up the dropdown menu
    #
    def __init__(self, default_text="", items=[], max_display_items=4):
        Gtk.Button.__init__(self)

        # Attach styling class name
        self.get_style_context().add_class("KanoComboBox")

        # the ComboBox is comprised of a Label for the selected item
        # and an arrow image to indicate a dropdown menu
        self.box = Gtk.Box()
        self.label = Gtk.Label(default_text)
        arrow = Gtk.Image()
        arrow.set_from_file(self.ARROW_DOWN)

        # we pack these widgets inside a box and use an empty label as a spacer
        self.box.pack_start(self.label, False, False, 10)
        self.box.pack_start(Gtk.Label(), True, True, 0)
        self.box.pack_start(arrow, False, False, 10)
        self.add(self.box)

        # creating the scroll up and down buttons for the dropdown menu
        self.scroll_up_button = self.ScrollMenuItem(self.SCROLL_ARROW_UP)
        self.scroll_down_button = self.ScrollMenuItem(self.SCROLL_ARROW_DOWN)
        self.scroll_up_button.connect("button-press-event", self.on_scroll_button)
        self.scroll_down_button.connect("button-press-event", self.on_scroll_button)

        # creating the popup dropdown menu
        self.dropdown = Gtk.Menu()
        self.dropdown.set_size_request(self.WIDTH, -1)

        # we'll need to receive notifications about scrolling events
        self.dropdown.add_events(Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.SMOOTH_SCROLL_MASK)
        self.dropdown.connect("scroll-event", self.on_scroll)

        # this variable will index the first displayed dropdown items
        # items to be displayed will then be in the range [first, first + max]
        self.first_item_index = 0

        # initialising the dropdown menu with the given max number of items to display
        self.max_display_items = max_display_items
        self.set_items(items)

        # setting the widget's variables
        self.selected_item_index = -1
        self.selected_item_text = ""

        # when the combobox button is clicked, we popup the dropdown
        self.connect("button-press-event", self.on_combo_box_click)

    def include_styling(self):
        self.provider = Gtk.CssProvider()
        path = os.path.join(common_css_dir, "kano_combobox.css")
        self.provider.load_from_path(path)

        apply_styles()

        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def on_combo_box_click(self, widget, event):
        self.emit("popup")

        # display all items in the dropdown menu and popup
        self.dropdown.show_all()
        self.dropdown.popup(None, None, self.popup_set_position, None, event.button, event.time)

    def popup_set_position(self, menu, data):
        # this is used by the popup() method to get the drawing x,y coordinates
        # we make it so that it is positioned just underneath the combobox button
        window = self.get_window()
        (_, window_x, window_y) = window.get_origin()
        combobox_x = self.get_allocation().x + window_x
        combobox_y = self.get_allocation().y + window_y
        combobox_height = self.get_allocation().height

        return combobox_x, combobox_y + combobox_height, True

    def on_scroll(self, widget, event):
        # distinguishing between scrolling up and down
        if event.direction == Gdk.ScrollDirection.UP:
            self.on_scroll_up()
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.on_scroll_down()

    def on_scroll_button(self, button, event):
        # triggered when a scroll button has just been pressed (not released)
        if button == self.scroll_up_button:
            self.on_scroll_up()
        elif button == self.scroll_down_button:
            self.on_scroll_down()

    def on_scroll_up(self):
        # making sure we don't go out of range
        if self.first_item_index == 0:
            return

        # 'scroll up' in the items list and 'refresh' the dropdown
        self.first_item_index -= 1
        self.update_dropdown()

    def on_scroll_down(self):
        # making sure we don't go out of range
        if self.first_item_index >= len(self.items) - self.max_display_items:
            return

        # 'scroll up' in the items list and 'refresh' the dropdown
        self.first_item_index += 1
        self.update_dropdown()

    def update_dropdown(self):
        # first, remove all items inside the dropdown menu
        for item in self.dropdown.get_children():
            self.dropdown.remove(item)

        # first item in the dropdown menu is the scroll up image button
        self.dropdown.append(self.scroll_up_button)

        # make sure we do not overflow - this may happen if e.g. we have 3 items and display 5
        if self.first_item_index + self.max_display_items > len(self.items):
            last_display_item = len(self.items)
        else:
            last_display_item = self.first_item_index + self.max_display_items

        # then add to the dropdown the items to be displayed in the new range
        for index in range(self.first_item_index, last_display_item):
            item = Gtk.MenuItem(self.items[index])
            item.connect("activate", self.on_item_selected, index)
            self.dropdown.append(item)

        # last item in the dropdown menu is the scroll down image button
        self.dropdown.append(self.scroll_down_button)

        # redisplay all the new items
        self.dropdown.show_all()

    def on_item_selected(self, item, index):
        changed = False
        if self.selected_item_index != index:
            changed = True

        # item is the MenuItem which was selected
        # and it's corresponding index in self.items
        self.selected_item_index = index
        self.selected_item_text = item.get_label()
        self.label.set_text(item.get_label())

        self.emit("selected")
        if changed:
            self.emit("changed")

    def get_selected_item_index(self):
        # returns the index of the selected item in the list of items given
        # or -1 if no item was selected
        return self.selected_item_index

    def get_selected_item_text(self):
        # return the text of the selected item
        return self.selected_item_text

    def set_selected_item_index(self, index):
        # use this to select an item from the items list
        self.selected_item_index = index
        self.label.set_text(self.items[index])
        self.selected_item_text = self.items[index]

    def set_text(self, text):
        # use this to set the text of the combobox directly
        # NOTE: this does not modify the actual selected item index and/or text!
        self.label.set_text(text)

    def get_items(self):
        # use this to retrieve the list of string items
        return self.items

    def set_items(self, items):
        # use this to set a list of string items for the dropdown menu
        # it makes sure the parameter is actually a List which contains Strings
        if not isinstance(items, types.ListType):
            raise TypeError("KanoComboBox: set_items(): You must supply a List when setting items")

        for item in items:
            if not isinstance(item, types.StringTypes):
                raise TypeError("KanoComboBox: append(): You must supply a String when appending text")

        self.items = list(items)
        self.update_dropdown()

    def append(self, text):
        # use this to append items to the dropdown menu
        if not isinstance(text, types.StringTypes):
            raise TypeError("KanoComboBox: append(): You must supply a String when appending text")
        self.items.append(text)
        self.update_dropdown()

    def remove_all(self):
        # use this to remove all items from the dropdown - will reset selected item
        self.items = list()
        self.first_item_index = 0
        self.selected_item_index = -1
        self.selected_item_text = ""
        self.label.set_text("")
        self.update_dropdown()

    # @Override
    def set_size_request(self, width, height):
        self.dropdown.set_size_request(width, -1)
        return Gtk.Button.set_size_request(self, width, height)

    def do_popup(self):
        # print 'dropdown popup'
        pass

    def do_popdown(self):
        # print 'dropdown popdown'
        pass

    def do_selected(self):
        # print 'new item selected'
        pass

    def do_changed(self):
        # print 'new item changed'
        pass

    class ScrollMenuItem(Gtk.ImageMenuItem):

        def __init__(self, image_path):
            Gtk.ImageMenuItem.__init__(self)
            self.set_use_underline(False)
            self.set_always_show_image(True)

            # set the given image
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
            image = Gtk.Image.new_from_pixbuf(pixbuf)

            # put the image inside an alignment container for centering
            self.box = Gtk.Alignment()
            self.box.set_padding(0, 0, 0, pixbuf.get_width())
            self.box.add(image)

            # by default, a MenuItem has an AccelLabel widget as it's one and only child
            self.remove(self.get_child())
            self.add(self.box)

            # By overriding this signal we can stop the Menu
            # containing this item from being popped down
            self.connect("button-release-event", self.do_not_popdown_menu)

        def do_not_popdown_menu(self, widget, event):
            # Return that the signal has been handled
            # Subsequent default handling routines will not be executed
            return True


# Test class

class TestComboBoxWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.combo_box = KanoComboBox()

        self.combo_box.include_styling()

        self.add(self.combo_box)
        self.combo_box.set_items(["item1", "item2", "item3", "item4", "item5", "item6", "item7", "item8"])
        self.combo_box.set_selected_item_index(0)

        self.connect("delete-event", Gtk.main_quit)

        self.show_all()


if __name__ == "__main__":
    win = TestComboBoxWindow()
    Gtk.main()
