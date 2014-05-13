# Kanux-utils

Collection of utilities

## kano-launcher

Launches the app passed as an argument

## kano-shutdown

Script to shutdown the system after a confirmation message on the graphic frontend.
The user needs sudo NOPASSWD: privileges for /sbin/poweroff.

## make-focus

This module gets called when Kano "Focus" key is pressed.
It finds the currently active window, decides if/where focus needs to go and switches focus.

This script is fired by openbox, it is registered in the lxde xml file, normally ~/config/openbox/lxde-rc.xml

This module requires the debian package: python-xlib
Code excerpts collected from: http://thp.io/2007/09/x11-idle-time-and-focused-window-in.html
For sending keys: http://autokey.googlecode.com/svn-history/r8/trunk/autokey.py
API documentation: http://python-xlib.sourceforge.net/doc/html/python-xlib_16.html

Returns 0 if no focus action has taken place, non-zero otherwise.

## rpi-info

Displays a report of hardware details of a RaspberryPI unit.
Code parts taken from: http://elinux.org/RPI_vcgencmd_usage
