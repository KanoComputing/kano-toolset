# decorators.py
#
# Copyright (C) 2015-2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Decorators used to simplify control and ease modularity


import os
import sys
import time
import math
from functools import wraps

from kano.logging import logger

ERR_ROOT_PERMISSIONS_REQ = -1


def require_root(exit_on_failure=False, verbose=False):
    '''
    Generates decorator to enforce root permissions

    NB: must be called when used as decorator, i.e.
        @require_root()
        def my_func():
            pass

    @params  exit_on_failure   Quit application on failure
    @params  verbose           Print messages to stdout
    '''

    def require_root_decorator(func):
        '''
        Actual decorator that gets applied to functions
        '''

        @wraps(func)
        def ensure_root(*args, **kwargs):
            if os.getuid() != 0:
                msg = 'You need to run this option as root, try with sudo'
                logger.error(msg)

                if verbose:
                    sys.stdout.write('{}\n'.format(msg))

                if exit_on_failure:
                    sys.exit(ERR_ROOT_PERMISSIONS_REQ)

                return False

            return func(*args, **kwargs)

        return ensure_root

    return require_root_decorator


def retry(tries, delay=3, backoff=2):
    '''
    Taken from the sample decorators at:
        https://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    Copyright retained by owners of wiki.python.org

    Retries a function or method until it returns True.

    delay sets the initial delay in seconds, and backoff sets the factor by which
    the delay should lengthen after each failure. backoff must be greater than 1,
    or else it isn't really a backoff. tries must be at least 0, and delay
    greater than 0.'''

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    tries = math.floor(tries)
    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay  # make mutable

            rv = f(*args, **kwargs)  # first attempt
            while mtries > 0:
                if rv is True:  # Done on success
                    return True

                mtries -= 1  # consume an attempt
                time.sleep(mdelay)  # wait...
                mdelay *= backoff  # make future wait longer

                rv = f(*args, **kwargs)  # Try again

            return False  # Ran out of tries :-(

        return f_retry  # true decorator -> decorated function
    return deco_retry  # @retry(arg[, ...]) -> true decorator


def queue_cb(callback, callback_args=None, callback_kwargs=None, gtk=False):
    '''
    Run the supplied callback after the function completes

    @param  callback          Function to run upon completion
    @param  callback_args     Arguments to send to the callback
    @param  callback_kwargs   Keyword arguments to send to the callback
    @param  gtk               Should the callback be run for Gtk
    '''

    callback_args = callback_args or []
    callback_kwargs = callback_kwargs or {}

    if gtk:
        from gi.repository import GObject
        callback_args.insert(0, callback)
        callback = GObject.idle_add

    def cb_decorator(func):
        @wraps(func)
        def run_cb(*args, **kwargs):
            func(*args, **kwargs)

            return callback(*callback_args, **callback_kwargs)

        return run_cb

    return cb_decorator
