#!/usr/bin/env python

# window.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: GNU General Public License v2 http://www.gnu.org/licenses/gpl-2.0.txt
#
# Base common code for Kano apps and projects
#

from gi.repository import GdkX11, Gdk
import Xlib.display
import time

from kano.utils import run_cmd

BOTTOM_BAR_HEIGHT = 44

def _get_win_property(gdk_win, property_name):
    disp = Xlib.display.Display()
    xwin = disp.create_resource_object("window", gdk_win.get_xid())

    for i in range(0, 10):
        prop = xwin.get_full_property(disp.intern_atom(property_name), Xlib.X.AnyPropertyType)
        if prop is not None:
            disp.close()
            return prop.value
        time.sleep(0.1)

    disp.close()


# Extremly hackish, but the most reliable way of determining
# whether the window is decorated by the window manager
def _is_decorated(win):
    if not win:
        return

    extents = _get_win_property(win, "_NET_FRAME_EXTENTS")
    if extents:
        return sum(extents) > 0
    else:
        return False


# Returns a 2-tuple (width, height) that is used for decoration
def _get_decoration_size(win):
    if not win:
        return
    extents = _get_win_property(win, "_NET_FRAME_EXTENTS")
    if extents:
        return (extents[0] + extents[1], extents[2] + extents[3])
    else:
        return 0


def _get_window_by_pid(pid):
    root = Gdk.get_default_root_window()
    if not root:
        return
    extents = _get_win_property(root, '_NET_CLIENT_LIST')
    if not extents:
        return

    for id in extents:
        w = GdkX11.X11Window.foreign_new_for_display(Gdk.Display.get_default(), id)
        if w:
            wm_pids = _get_win_property(w, "_NET_WM_PID")
            if pid in wm_pids:
                return w


def _get_window_by_child_pid(pid):
    root = Gdk.get_default_root_window()
    if not root:
        return
    extents = _get_win_property(root, '_NET_CLIENT_LIST')
    if not extents:
        return

    # make a set of all visible pids
    winpids = set()
    for id in extents:
        w = GdkX11.X11Window.foreign_new_for_display(Gdk.Display.get_default(), id)
        if w:
            for pid in _get_win_property(w, "_NET_WM_PID")[2]:
                winpids.add(pid)

    # make a list of (pid, pstree_section) pairs
    winpid_trees = []
    for winpid in winpids:
        cmd = 'pstree -pl {}'.format(winpid)
        o, _, _ = run_cmd(cmd)
        if '({})'.format(pid) in o:
            winpid_trees.append((winpid, o))

    if not winpid_trees:
        return

    # sort the list by the pstree length
    winpid_trees = sorted(winpid_trees, key=lambda k: len(k[1]), reverse=False)
    winpid = winpid_trees[0][0]

    # get win belonging to that pid
    for id in extents:
        w = GdkX11.X11Window.foreign_new_for_display(Gdk.Display.get_default(), id)
        if w:
            wm_pids = _get_win_property(w, "_NET_WM_PID")
            if winpid in wm_pids:
                return w


def _get_window_by_title(title):
    root = Gdk.get_default_root_window()
    if not root:
        return
    extents = _get_win_property(root, '_NET_CLIENT_LIST')
    if not extents:
        return

    for id in extents:
        w = GdkX11.X11Window.foreign_new_for_display(Gdk.Display.get_default(), id)
        if w:
            wm_name = _get_win_property(w, "WM_NAME")
            if wm_name and title == wm_name:
                return w


def _get_window_by_id(wid):
    if wid[0:2] == "0x":
        wid = int(wid, 16)
    return GdkX11.X11Window.foreign_new_for_display(Gdk.Display.get_default(), int(wid))


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
    scr_width = Gdk.Screen.width()
    scr_height = Gdk.Screen.height() - BOTTOM_BAR_HEIGHT

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
                Gdk.Window.process_all_updates()
                Gdk.flush()
        else:
            # Resize if the window was not decorated before
            if not _is_decorated(win):
                win.set_decorations(1)
                Gdk.flush()

                dw, dh = _get_decoration_size(win)
                old_width -= dw
                old_height -= dh

    # Resizing is irrelevant when maximizing, so just return afterwards
    if maximized:
        win.maximize()
        Gdk.Window.process_all_updates()
        Gdk.flush()
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
    Gdk.Window.process_all_updates()
    Gdk.flush()
