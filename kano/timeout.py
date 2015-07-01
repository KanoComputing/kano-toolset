# The timeout decorator
#
# Copyright (C) 2015 Kano Computing Ltd.
# License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Allows to run functions with a specified timeout easily.
#
# Source:
#   http://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish
#
# Usage:
#
#   @timeout(10) #seconds
#   def your_function(a, b):
#       ...
#
#   The function will be interrupted after the specified timeout

from functools import wraps
import errno
import os
import signal


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator
