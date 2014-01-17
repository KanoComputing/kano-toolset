#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: GNU General Public License v2 http://www.gnu.org/licenses/gpl-2.0.txt
#
# Author: Radek Pazdera <radek@kano.me>
# Description: Base common code for Kano apps and projects

import gtk
from gtk import gdk

import webkit
import sys
import re
import os
import urllib
import warnings
import time

BOTTOM_BAR_HEIGHT = 39

# Extremly hackish, but the most reliable way of determining
# whether the window is decorated by the window manager
def _is_decorated(win):
    extents = win.property_get("_NET_FRAME_EXTENTS")[2]
    return sum(extents) > 0

# Returns a 2-tuple (width, height) that is used for decoration
def _get_decoration_size(win):
    extents = win.property_get("_NET_FRAME_EXTENTS")[2]
    return (extents[0] + extents[1], extents[2] + extents[3])

def _get_window_by_pid(pid):
    root = gdk.get_default_root_window()
    for id in root.property_get('_NET_CLIENT_LIST')[2]:
        w = gdk.window_foreign_new(id)
        if w:
            wm_pids = w.property_get("_NET_WM_PID")
            if pid in wm_pids[2]:
                return w

def _get_window_by_title(title):
    root = gdk.get_default_root_window()
    for id in root.property_get('_NET_CLIENT_LIST')[2]:
        w = gdk.window_foreign_new(id)
        if w:
            wm_name = w.property_get("WM_NAME")
            if wm_name and title == wm_name[2]:
                return w

def _get_window_by_id(wid):
    if wid[0:2] == "0x":
        wid = int(wid, 16)
    return gdk.window_foreign_new(int(wid))

# Find the gdk window to be manipulated. Gives up after 30 seconds.
def find_window(title=None, pid=None, wid=None):
    if title == None and pid == None and wid == None:
        raise ArgumentError("At least one identificator needed.")

    win = None
    for i in range(1, 300):
        if title != None:
            win = _get_window_by_title(title)
        elif pid != None:
            win = _get_window_by_pid(pid)
        else:
            win = _get_window_by_id(wid)

        if win != None:
            break
        time.sleep(0.1)
    return win

def gdk_window_settings(win, x=None, y=None, width=None, height=None,
                        decoration=None, maximized=False, centered=False):
    # Screen dimensions
    scr_width = gdk.screen_width()
    scr_height = gdk.screen_height() - BOTTOM_BAR_HEIGHT

    # Window dimensions and position
    old_x, old_y = win.get_root_origin()
    old_width, old_height = win.get_geometry()[2:4]

    # Sort out the decorations
    if decoration != None:
        if decoration == False:
            # Resize if the window was decorated before
            if _is_decorated(win):
                dw, dh = _get_decoration_size(win)
                old_width += dw
                old_height += dh

                win.set_decorations(0)
                gdk.window_process_all_updates()
                gdk.flush()
        else:
            # Resize if the window was not decorated before
            if not _is_decorated(win):
                win.set_decorations(1)
                gdk.flush()

                dw, dh = _get_decoration_size(win)
                old_width -= dw
                old_height -= dh

    # Resizing is irrelevant when maximizing, so just return afterwards
    if maximized:
        win.maximize()
        gdk.window_process_all_updates()
        gdk.flush()
        return

    # Initialize the target values
    new_x, new_y, new_width, new_height = old_x, old_y, old_width, old_height

    # Window position
    if x != None:
        if x <= 1:
            new_x = scr_width * x
        else:
            new_x = x

    if y != None:
        if y <= 1:
            new_y = scr_height * y
        else:
            new_y = y

    # Window dimensions
    if width != None:
        if width <= 1:
            new_width = scr_width * width
        else:
            new_width = width

        if decoration == True:
            new_width -= _get_decoration_size(win)[0]

    if height != None:
        if height <= 1:
            new_height = scr_height * height
        else:
            new_height = height
        
        if decoration == True:
            new_height -= _get_decoration_size(win)[1]

    # Should the window be centered?
    if centered:
        dec_w, dec_h = _get_decoration_size(win)
        new_x = (scr_width - new_width - dec_w) / 2
        new_y = (scr_height - new_height - dec_h) / 2

    # Do all the resizing at once
    win.move_resize(int(new_x), int(new_y), int(new_width), int(new_height))
    gdk.window_process_all_updates()
    gdk.flush()


class WebApp(object):
    _index = None
    _title = "Application"

    # Window properties
    _x = None
    _y = None
    _width = None
    _height = None
    _centered = False
    _maximized = False
    _decoration = True

    def run(self):
        warnings.simplefilter("ignore")

        self._view = view = webkit.WebView()
        view.connect('navigation-policy-decision-requested',
                     self._api_handler)
        view.connect('close-web-view', self._close)

        if hasattr(self.__class__, "_focus_in"):
            view.connect('focus-in-event', self._focus_in)

        if hasattr(self.__class__, "_focus_out"):
            view.connect('focus-out-event', self._focus_out)

        sw = gtk.ScrolledWindow()
        sw.add(view)

        self._win = win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.set_title(self._title)
        win.connect("destroy", gtk.main_quit)

        win.add(sw)
        win.realize()
        win.show_all()

        gdk_window_settings(win.window, self._x, self._y,
                            self._width, self._height, self._decoration,
                            self._maximized, self._centered)

        view.open(self._index)

        gtk.main()

    def exit(self):
        sys.exit(0)

    def error(self, msg):
       sys.stderr.write("Error: %s\n" % msg)

    def chooseFile(self, default_dir=None):
        dialog = gtk.FileChooserDialog("Open File",
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                       gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        dialog.set_default_response(gtk.RESPONSE_OK)
 
        filter = gtk.FileFilter()
        filter.set_name("XML Files")
        filter.add_pattern("*.xml")
        dialog.add_filter(filter)

        if default_dir != None:
            dialog.set_current_folder(os.path.expanduser(default_dir))

        path = ""

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            path = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            self.error("No files selected.")

        dialog.destroy()

        return path

    def readFile(self, path):
        try:
            with open(path, "r") as f:
                return f.read()
        except:
            self.error("Unable to open file '%s'." % path)
            return ""

    def _close(self, view, data=None):
        sys.exit(0)

    def _parse_api_call(self, call_str):
        call_re = r"#api:(\w+)(\[\d+\])?(/[^/]*)*$"
        call_match = re.search(call_re, call_str)

        name = call_match.group(1)
        call = [name]
        timestamp = call_match.group(2)
        if timestamp != None:
            call.append(timestamp[1:-1])
        else:
            call.append(None)

        args = re.sub(r"^#api:[^/]*/?", r"", call_match.group(0))

        if len(args) > 0:
            if args[-1] == "/":
                args = args[:-1]
            call += map(urllib.unquote, args.split("/"))

        return call

    def _api_handler(self, view, frame, request, action, decision, data=None):
        uri = action.get_original_uri()

        # Not an api call, let webkit handle it
        if re.search("#api:", uri) == None:
            return False
        
	func_data = self._parse_api_call(uri)

        name = func_data[0]
        timestamp = func_data[1]
        args = func_data[2:]

        try:
            func = getattr(self, name)
        except AttributeError:
            self.error("API method '%s' doesn't exist!" % name)
            return True

        if len(args) > 0:
            retval = func(*args)
        else:
            retval = func()

        if timestamp != None:
            if retval == None:
                retval = "null"
            elif type(retval) == int or type(retval) == float:
                retval = str(retval)
            elif type(retval) == str:
                print retval
                retval = "\"" + urllib.quote(retval, "") + "\""
                print retval

            script = "backend.trigger_cb(\"%s\", %s, %s);"
            view.execute_script(script % (name, timestamp, retval))

        return True
