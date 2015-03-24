# kano.logging
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2

# Start the python debugger
def start_term(a, b):
    import pdb
    pdb.set_trace()


# start the python debugger for remote connection on port 444
# needs pip install remote_pdb
def start_remote(a, b):
    from remote_pdb import RemotePdb
    RemotePdb('0.0.0.0', 4444).set_trace()


# start the debugger on a tty

# for some reason this needs you to do chvt 8
# before you can switch to vt 8 with the keyboard
def start_tty(a, b, tty="/dev/tty8"):
    from pdb import Pdb
    io = open(tty, "r+b")
    Pdb(stdin=io, stdout=io).set_trace()


# Start pdb in an rxvt on X
def start_x(a, b):
    from pdb import Pdb
    import os
    from pty import openpty

    (master, slave) = openpty()
    cmd = "rxvt -pty-fd {} &".format(master)
    os.system(cmd)
    io = os.fdopen(slave, "r+b")
    Pdb(stdin=io, stdout=io).set_trace()


# set a handler on SIGUSR1. NB although all the above shoudln't really
# work as signal handlers, because they call system calls which you are
# not supposed to use in a handler, these are okay because in fact
# python is handling the signal in C then interpreting these 'handlers'
# outside the handler.

# To use: pydebug.patch_handler(pydebug.start_x)
def patch_handler(handler):
    import signal
    signal.signal(signal.SIGUSR1, handler)
