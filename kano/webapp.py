#!/usr/bin/env python

# webapp.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import gtk
import webkit
import sys
import re
import os
import urllib
import warnings
import subprocess

from kano.window import gdk_window_settings


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
        dialog = gtk.FileChooserDialog(
            "Open File",
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
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
                retval = "\"" + urllib.quote(retval, "") + "\""

            script = "backend.trigger_cb(\"%s\", %s, %s);"
            view.execute_script(script % (name, timestamp, retval))

        return True
