# kano.logging
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

'''
This module provides the core Kano Logging functionality
However it is actually a lazy loader for kano._logging
'''

import sys

# The way this module works is that the 'kano.logging' entry in sys.modules gets substituted twice:
# First, with the loader class below
# When an attribute on that class is accessed, it gets substituted a second time.

class lazy_logger:
    def __getattr__(self, name):
        import kano._logging
        return getattr(kano._logging.logger, name)


class loader:
    ll = lazy_logger

    def __init__(self, old_mod):
        self.old_mod = old_mod

    def __getattr__(self, name):
        # avoid importing the module just to make a logger object
        if name == '__path__':
            return getattr(self.old_mod, name)

        if name == 'logger':
            return self.ll()

        # load the real module
        # at this point we have substituted the module once,
        # so we need to import sys again
        import sys
        import kano._logging  

        lm = sys.modules['kano._logging']
        sys.modules[__name__] = lm
        return getattr(lm, name)


def log_excepthook(exc_class, exc_value, tb):
    # at this point we have substituted the module once,
    # so we need to import all modules again
    import traceback
    import kano.logging # Don't think about this one too hard...
    import sys

    tb_txt = ''.join(traceback.format_tb(tb))
    try:
        (filename, number, function, line_text) = traceback.extract_tb(tb)[-1]
        exc_txt = "{} line {} function {} [{}]".format(
            filename, number, function, line_text)
    except:
        exc_txt = ""

    kano.logging.logger.error("Unhandled exception '{}' at {} (see logfile for full trace)"
                 .format(exc_value, exc_txt),
                 traceback=tb_txt,
                 exc_class=str(exc_class),
                 exc_value=str(exc_value))
    sys.__excepthook__(exc_class, exc_value, tb)

sys.excepthook = log_excepthook

# substitute the lazy loader module
sys.modules[__name__] = loader(sys.modules[__name__])
