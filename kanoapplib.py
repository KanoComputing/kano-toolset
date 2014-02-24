#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: GNU General Public License v2 http://www.gnu.org/licenses/gpl-2.0.txt
#
# Base common code for Kano apps and projects
#

import gtk
from gtk import gdk

import webkit
import sys
import re
import os
import urllib
import warnings
import time
import subprocess

BOTTOM_BAR_HEIGHT = 39


# Get property needs to run through a loop in case the
# window is not yet ready
def _get_win_property(win, property_name):
    for i in range(0, 10):
        property = win.property_get(property_name)
        if property is not None:
            return property[2]
        time.sleep(0.1)
    return None


# Extremly hackish, but the most reliable way of determining
# whether the window is decorated by the window manager
def _is_decorated(win):
    extents = _get_win_property(win, "_NET_FRAME_EXTENTS")
    return sum(extents) > 0


# Returns a 2-tuple (width, height) that is used for decoration
def _get_decoration_size(win):
    extents = _get_win_property(win, "_NET_FRAME_EXTENTS")
    return (extents[0] + extents[1], extents[2] + extents[3])


def _get_window_by_pid(pid):
    root = gdk.get_default_root_window()
    extents = _get_win_property(root, '_NET_CLIENT_LIST')
    for id in extents:
        w = gdk.window_foreign_new(id)
        if w:
            wm_pids = w.property_get("_NET_WM_PID")
            if pid in wm_pids[2]:
                return w


def _get_window_by_title(title):
    root = gdk.get_default_root_window()
    extents = _get_win_property(root, '_NET_CLIENT_LIST')
    for id in extents:
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
    if (title is None) and (pid is None) and (wid is None):
        raise ValueError("At least one identificator needed.")

    win = None
    for i in range(1, 300):
        if title is not None:
            win = _get_window_by_title(title)
        elif pid is not None:
            win = _get_window_by_pid(pid)
        else:
            win = _get_window_by_id(wid)

        if win is not None:
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
    if decoration is not None:
        if decoration is False:
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
    if x is not None:
        if x <= 1:
            new_x = scr_width * x
        else:
            new_x = x

    if y is not None:
        if y <= 1:
            new_y = scr_height * y
        else:
            new_y = y

    # Window dimensions
    if width is not None:
        if width <= 1:
            new_width = scr_width * width
        else:
            new_width = width

        if decoration is True:
            new_width -= _get_decoration_size(win)[0]

    if height is not None:
        if height <= 1:
            new_height = scr_height * height
        else:
            new_height = height

        if decoration is True:
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

    _zenity = None

    def run(self):
        warnings.simplefilter("ignore")

        zenity_cmd = ["zenity", "--progress", "--no-cancel",
                      "--title=Loading",
                      "--text=Loading...",
                      "--width=300", "--height=90", "--auto-close",
                      "--timeout=10", "--auto-kill"]

        self._zenity = subprocess.Popen(zenity_cmd, stdin=subprocess.PIPE)
        zin = self._zenity.stdin
        zin.write("20\n")

        self._view = view = webkit.WebView()
        view.connect('navigation-policy-decision-requested',
                     self._api_handler)
        view.connect('close-web-view', self._close)
        view.connect('onload-event', self._onload)

        # FIXME: The Inspector cannot be closed once opened.
        # The following line should be commented out for release until we fix this.
        # view.get_settings().set_property("enable-developer-extras", True)

        if hasattr(self.__class__, "_focus_in"):
            view.connect('focus-in-event', self._focus_in)

        if hasattr(self.__class__, "_focus_out"):
            view.connect('focus-out-event', self._focus_out)

        zin.write("40\n")

        splitter = gtk.VPaned()
        sw = gtk.ScrolledWindow()
        sw.add(view)
        splitter.add1(sw)

        inspector = view.get_web_inspector()
        inspector.connect("inspect-web-view", self._activate_inspector, splitter)

        zin.write("50\n")

        self._win = win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.set_title(self._title)
        win.connect("destroy", gtk.main_quit)

        zin.write("70\n")

        win.add(splitter)
        win.realize()
        win.show_all()

        gdk_window_settings(win.window, self._x, self._y,
                            self._width, self._height, self._decoration,
                            self._maximized, self._centered)

        zin.write("90\n")

        view.open(self._index)

        zin.write("99\n")

        gtk.main()

    def _activate_inspector(self, inspector, target_view, splitter):
        inspector_view = webkit.WebView()
        splitter.add2(inspector_view)
        return inspector_view

    def _onload(self, wv, frame, user_data=None):
        if self._zenity:
            try:
                self._zenity.stdin.write("100\n")
            except:
                pass
            del self._zenity

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

        if default_dir is not None:
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
        if timestamp is not None:
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
        if re.search("#api:", uri) is None:
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

        if timestamp is not None:
            if retval is None:
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
