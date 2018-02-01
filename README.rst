Kano Toolset
------------

|Coverage|

Collection of utilities for the RaspberryPI and KanoOS.

Most tools are used by the UI apps provided by the system, and their
interactions. But you can still use many of them to your own needs.
Below is a summary of the most remarkable ones.


Tiny tools under ``bin``
------------------------

``kano-camera`` lets you turn on and off the PiCamera. ``kano-dialog``
and ``kano-progress`` is used to display popup messages with a Kano look
& feel ``kano-led`` will blink your RaspberryPI board LED repeatedly for
a few seconds. ``kano-logs`` allows to inspect the system logs used by
all KanoOS applications ``kano-shutdown`` shuts down the system after a
confirmation message on the graphic frontend. ``kano-signal`` allows to
send save, load, share, and make signals to Kano apps ``rpi-info`` will
give you core information from you RPI unit such as CPU speed,
temperature, etc. ``bash`` this directory contains code wrappers to make
it easy to log events from Bash shell scripts.


Kano keys pressed
-----------------

A tool that returns an indication on wether the Ctrl-Alt key combination
is currently pressed. This tool is used to regain control on RaspberryPI
unsupported screens, and switch to a *safe mode*.


Kano Splash
-----------

``kano-splash`` is a tool to show very fast popup messages based on
image bitmaps. It uses the RaspberryPI GPU directly so it's very fast,
and it sits on top of all desktop apps.


kano-launcher
-------------

Launches KanoOS project apps, and allows for an organized termination
afterwars.


Kano Toolset Python bindings
----------------------------

The ``kano`` directory contains a lot of useful functions to do small
tasks on the OS. It is used widely across all Kano apps. They can be
easily imported from python e.g.
``from kano.utils import get_rpi_model; print get_rpi_model()``

The ``gtk3`` subdirectory contains a collection of UI widgets with a
uniform Kano look & feel. Gtk styles used across these are located under
the ``media`` directory.


Network setup scripts
---------------------

Connecting to the network requires some extra steps on Kano OS.

-  Setting the timezone depending on your geographic location
-  Setting the local time from a remote time server
-  Starting a server to apply network restrictions in Parental Mode
-  Checking for system updates availability to inform the user

Therefore, a custom dhcp hook is installed under
``/lib/dhcpcd/dhcpcd-hooks/``, which starts these tasks in the
background. A debug version is also available under
``/usr/share/kano-toolset/dhcpcd-hooks`` to diagnose any issues.

These hooks allow for the system to reconnect automatically to the
Wireless Access Point. The tool ``kano-test-dhcp`` is now provided which
can be used to make sure the steps above run correctly.

Network connection through Ethernet is managed by the system itself,
thanks to ifplugd. For wireless networking, the ``kano-connect`` program
handles the WPA supplicant startup when needed, which is configured
through the GUI app ``kano-wifi-gui``.

The classic Debian file ``/etc/network/interfaces`` is not used anymore.
It can still be installed manually should the kit need a special
configuration, like a fixed IP address.


uinput
------

This tool allows for sending keyboard events into the system, as if they
were pressed by the user.


iospeed (internal)
------------------

The script is a handy set of steps to compute your SD Card Input/Output
throughput.


kano-shutdown
-------------

Script to shutdown the system after a confirmation message on the
graphic frontend. The user needs sudo NOPASSWD: privileges for
/sbin/poweroff.


webapp
------

A webkit based browser is provided under ``kano/wepapp``. This component
is used from all Kano Blocks apps, mainly Make Pong and Make Minecraft
to provide the user interaction panel.

The Javascript module ``js/backend-api.js`` is used as a hack in wepapp
to provide for download callbacks necessary to download content from
Kano World.

.. |Coverage| image:: http://dev.kano.me/public/status-badges/kano-toolset-coverage.svg
   :target: http://dev.kano.me/public/status-badges/kano-toolset-coverage.svg
