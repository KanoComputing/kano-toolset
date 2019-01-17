#
# xwindow.py
#
# Copyright (C) 2015-2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# low level Xlib utilities
#
# Be careful mixing calls to this with Gtk.

from contextlib import contextmanager
import Xlib.display
from kano.logging import logger


def handle_uncaught_errors(err, req):
    # req is always None in the default error handler
    logger.error("error from Xlib {}".format(err))


@contextmanager
def display():
    '''
     A context manager for  display
    '''
    d = Xlib.display.Display()
    d.set_error_handler(handle_uncaught_errors)

    yield d

    d.close()


def find_xwindow_by_id(xid, parent):
    '''
    Given a parent Xlib Window, find a window with given xid
    returning Xlib window object
    '''
    try:
        for c in parent.query_tree().children:
            if c.id == xid:
                return c
            r = find_xwindow_by_id(xid, c)
            if r is not None:
                return r
    except Exception:
        return None


def xid_to_str(xid):
    ''' make a strign suitable for passing on command line'''

    return hex(xid).rstrip('L')

# NB this function opens its own X connection. This is only safe because
# we don't return any objects, only xids. Normally Xlib objects must be used
# in the context of a Display().


def get_child_windows_from_xid(xid):
    '''
    Given an X window id, return the xid's of its children
    '''
    try:
        with display() as d:
            root = d.screen().root
            xw = find_xwindow_by_id(xid, root)
            children = []
            for c in xw.query_tree().children:
                children.append(xid_to_str(c.id))
            return children
    except Exception:
        return []
