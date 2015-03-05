#!/usr/bin/python

"""
PyInputEvent provides a few convenience classes and methods to
read from Linux's event subsystem.

You probably want to create your own Controller class, inheriting
HIController

From the project at: https://github.com/rmt/pyinputevent

"""

import datetime
import os.path
import struct
import sys
import time
import ctypes

__voidptrsize = ctypes.sizeof(ctypes.c_voidp)
_64bit = (__voidptrsize == 8)
_32bit = (__voidptrsize == 4)
if _64bit:
    INPUTEVENT_STRUCT = "=LLLLHHl"
    INPUTEVENT_STRUCT_SIZE = 24
elif _32bit: # 32bit
    INPUTEVENT_STRUCT = "=iiHHi"
    INPUTEVENT_STRUCT_SIZE = 16
else:
    raise RuntimeError("Couldn't determine architecture, modify " + __file__ +
                       " to support your system.")

class InputEvent(object):
    """
    A `struct input_event`. You can instantiate it with a buffer, in which
    case the method `unpack(buf)` will be called.  Or you can create an
    instance with `InputEvent.new(type, code, value, timestamp=None)`, which
    can then be packed into the structure with the `pack` method.
    """
    __slots__ = ('etype', 'ecode', 'evalue', 'time', 'nanotime')

    def __init__(self, buf=None):
        """By default, unpack from a buffer"""
        if buf:
            self.unpack(buf)

    def set(self, etype, ecode, evalue, timestamp=None):
        """Set the parameters of this InputEvent"""
        if timestamp is None:
            timestamp = time.time()
        self.time, self.nanotime = int(timestamp), int(timestamp%1*1000000.0)
        self.etype = etype
        self.ecode = ecode
        self.evalue = evalue
        return self

    @classmethod
    def new(cls, etype, ecode, evalue, time=None):
        """Construct a new InputEvent object"""
        e = cls()
        e.set(etype, ecode, evalue, time)
        return e

    @property
    def timestamp(self):
        return self.time + (self.nanotime / 1000000.0)

    def unpack(self, buf):
        if _64bit:
            self.time, t1, self.nanotime, t3, \
            self.etype, self.ecode, self.evalue \
            = struct.unpack_from(INPUTEVENT_STRUCT, buf)
        elif _32bit:
            self.time, self.nanotime, self.etype, \
            self.ecode, self.evalue \
            = struct.unpack_from(INPUTEVENT_STRUCT, buf)
        return self
    def pack(self):
        if _64bit:
            return struct.pack(INPUTEVENT_STRUCT, 
            self.time, 0, self.nanotime, 0,
            self.etype, self.ecode, self.evalue)
        elif _32bit:
            return struct.pack(INPUTEVENT_STRUCT, 
            self.time, self.nanotime,
            self.etype, self.ecode, self.evalue)
    def __repr__(self):
        return "<InputEvent type=%r, code=%r, value=%r>" % \
            (self.etype, self.ecode, self.evalue)
    def __str__(self):
        return "type=%r, code=%r, value=%r" % \
            (self.etype, self.ecode, self.evalue)
    def __hash__(self):
        return hash( (self.etype, self.ecode, self.evalue,) )
    def __eq__(self, other):
        return self.etype == other.etype \
            and self.ecode == other.ecode \
            and self.evalue == other.evalue

class SimpleDevice(object):
    """
    The SimpleDevice reads events from a /dev/input/event* device.
    """
    def __init__(self, device, name=None):
        self.device = device
        self.name = name or device
        self._fileno = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
        self.buf = ""
    def read(self):
        """
        Read up to 4096 bytes from the input device, and generate an
        InputEvent for every 24 (or 16) bytes (sizeof(struct input_event))
        """
        self.buf += os.read(self._fileno, 4096)
        while len(self.buf) >= INPUTEVENT_STRUCT_SIZE:
            self.receive(InputEvent(self.buf[:INPUTEVENT_STRUCT_SIZE]))
            self.buf = self.buf[INPUTEVENT_STRUCT_SIZE:]
    def receive(self, event):
        """
        `receive` is called with an event as each new InputEvent
        is read.
        """
        print self.name, event
        sys.stdout.flush()
    def fileno(self):
        return self._fileno
    def close(self):
        os.close(self._fileno)
        self._fileno = -1



class KeyEvent(object):
    def __init__(self, scancode=None, timestamp=None):
        self.scancode = scancode
        self.keycode = None
        self.keydown = False
        self.keyup = False
        self.timestamp = timestamp
    def __str__(self):
        return "KeyEvent %s (%s) %s" % (
            self.keycode, self.scancode,
            self.keydown and "down" or "up")

class MoveEvent(object):
    def __init__(self, timestamp=None):
        self.x = 0
        self.y = 0
        self.timestamp = timestamp
    def move(self, axis, value):
        if axis == 0:
            self.x = value
        else:
            self.y = value
    def __str__(self):
        return "MoveEvent(%d, %d)" % (self.x, self.y)

class Controller(object):
    def __init__(self, name):
        self.name = name
    def format_timestamp(self, timestamp, fmt="%Y-%m-%d.%H:%M.%f"):
        return datetime.datetime.fromtimestamp(float(timestamp))\
            .strftime(fmt)
    def format_event(self, event):
        return "%s %s" % (self.format_timestamp(event.timestamp), event)
    def handle_keyup(self, keyevent):
        print self.format_event(keyevent)
    def handle_keydown(self, keyevent):
        print self.format_event(keyevent)
    def handle_move(self, moveevent):
        print self.format_event(moveevent)
    def handle_events(self, events):
        for event in events:
            print self.format_event(event)

class HIDevice(SimpleDevice):
    """
    A HIDevice deals with both keyboard and mouse events.
    """
    def __init__(self, controller, *args, **kwargs):
        SimpleDevice.__init__(self, *args, **kwargs)
        self.controller = controller
        self.keys = []
        self.move = None
        self.events = []
    def receive(self, event):
        etype, ecode, evalue = (
            event.etype,
            event.ecode,
            event.evalue,
        )
        if etype == 2:
            if not self.move:
                self.move = MoveEvent(timestamp=event.timestamp)
            self.move.move(ecode, evalue)
        elif etype == 4:
            # initiate key event ? is evalue a scancode?
            pass
        elif etype == 1: # key
            key = KeyEvent(evalue, timestamp=event.timestamp)
            if evalue == 1: # keydown
                key.keydown = True
            else:
                key.keyup = True
            key.keycode = ecode
            self.keys.append(key)
        elif etype == 0:
            if self.move:
                self.controller.handle_move(self.move)
                self.move = None
            if self.keys:
                for key in self.keys:
                    if key.keydown:
                        self.controller.handle_keydown(key)
                    else:
                        self.controller.handle_keyup(key)
                self.keys = []
            if self.events:
                self.controller.handle_events(self.events)
                self.events = []
        else:
            self.events.append(event)

def main(args, controller=None):
    import select
    if controller is None:
        controller = Controller("Controller")
    fds = {}
    poll = select.poll()
    for dev in args:
        type, dev = dev.split(":",1)
        dev = HIDevice(controller, dev, type)
        fds[dev.fileno()] = dev
        poll.register(dev, select.POLLIN | select.POLLPRI)
    while True:
        for x,e in poll.poll():
            dev = fds[x]
            dev.read()

if __name__ == '__main__':
    main(sys.argv[1:])

# sudo python read.py mouse:/dev/input/event8 kbd:/dev/input/event6
