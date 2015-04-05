#!/usr/bin/env python

# window.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: GNU General Public License v2 http://www.gnu.org/licenses/gpl-2.0.txt
#

'''
Base common code for Kano apps and projects
'''

from gtk import gdk
import time

from kano.utils import run_cmd
import kano.xwindow

BOTTOM_BAR_HEIGHT = 44


# Get property needs to run through a loop in case the
# window is not yet ready
def _get_win_property(win, property_name):
    if not win:
        return

    for i in range(0, 10):
        property = win.property_get(property_name)
        if property:
            return property[2]
        time.sleep(0.1)
    return


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
    root = gdk.get_default_root_window()
    if not root:
        return
    extents = _get_win_property(root, '_NET_CLIENT_LIST')
    if not extents:
        return

    for id in extents:
        w = gdk.window_foreign_new(id)
        if w:
            wm_pids = w.property_get("_NET_WM_PID")
            if pid in wm_pids[2]:
                return w


def _get_window_by_child_pid(pid):
    root = gdk.get_default_root_window()
    if not root:
        return
    extents = _get_win_property(root, '_NET_CLIENT_LIST')
    if not extents:
        return

    # make a set of all visible pids
    winpids = set()
    for id in extents:
        w = gdk.window_foreign_new(id)
        if w:
            for pid in w.property_get("_NET_WM_PID")[2]:
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
        w = gdk.window_foreign_new(id)
        if w:
            wm_pids = w.property_get("_NET_WM_PID")
            if winpid in wm_pids[2]:
                return w


def _get_window_by_title(title):
    root = gdk.get_default_root_window()
    if not root:
        return
    extents = _get_win_property(root, '_NET_CLIENT_LIST')
    if not extents:
        return

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


def retry_for(fn, secs, *args, **kwargs):
    '''
    Retry a function for some time if it returns None
    '''
    res = None
    for i in range(1, secs * 10):
        res = fn(*args, **kwargs)
        if res is not None:
            return res
        time.sleep(0.1)
    return res


def find_window(title=None, pid=None, wid=None):
    '''
    Finds the gdk window identified by title, pid or wid (X window ID)
    to be manipulated. It gives up if it does not appear in 30 seconds.
    '''

    if (title is None) and (pid is None) and (wid is None):
        raise ValueError("At least one identificator needed.")

    win = retry_for(_find_window_any, 30, title=title, pid=pid, wid=wid)
    return win


def _find_window_any(title=None, pid=None, wid=None):
    '''
    Find the gdk window identified by title, pid or wid (X window ID)
    '''
    win = None
    if title is not None:
        win = _get_window_by_title(title)
    elif pid is not None:
        win = _get_window_by_pid(pid)
    else:
        win = _get_window_by_id(wid)
    return win


def get_child_windows(win):
    ''' Get child windows
        assumes that there is at least one, so waits for up to
        30 seconds for it to appear.
    '''
    child_xids = retry_for(
        kano.xwindow.get_child_windows_from_xid, 30, win.xid)
    return map(_get_window_by_id, child_xids)


def gdk_window_settings(win, x=None, y=None, width=None, height=None,
                        decoration=None, maximized=False, centered=False):
    '''
    Applies appeareance and position modifications to the Window identified by win    
    '''
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
