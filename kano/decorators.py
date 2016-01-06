# decorators.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Decorators used to simplify control and ease modularity


import os
import sys
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

        def ensure_root(*args, **kwargs):
            if os.getuid() != 0:
                msg = 'You need to run this option as root, try with sudo'
                logger.error(msg)

                if verbose:
                    print msg

                if exit_on_failure:
                    sys.exit(ERR_ROOT_PERMISSIONS_REQ)

                return False

            return func(*args, **kwargs)

        return ensure_root

    return require_root_decorator
