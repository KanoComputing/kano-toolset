# decorators.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Decorators used to simplify control and ease modularity


import os
from kano.logging import logger

def require_root(func):
    def ensure_root():
        if not os.getuid() == 0:
            logger.error('You need to run this option as root, try with sudo')
            return False

        return func()

    return ensure_root
