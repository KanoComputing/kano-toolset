# Kano Toolset

Collection of utilities for the RaspberryPI and KanoOS.

Most tools are used by the UI apps provided by the system, and their interactions.
But you can still use many of them to your own needs. Below is a summary of the most remarkable ones.

## Tiny tools under `bin`

`kano-camera` lets you turn on and off the PiCamera.
`kano-dialog` and `kano-progress` is used to display popup messages with a Kano look & feel
`kano-led` will blink your RaspberryPI board LED repeatedly for a few seconds.
`kano-logs` allows to inspect the system logs used by all KanoOS applications
`kan-shutdown` shuts down the system after a confirmation message on the graphic frontend.
`kano-signal` allows to send save, load, share, and make signals to Kano apps
`rpi-info` will give you core information from you RPI unit such as CPU speed, temperature, etc.


## Kano keys pressed

A tool that returns an indication on wether the Ctrl-Alt key combination is currently pressed.
This tool is used to regain control on RaspberryPI unsupported screens, and switch to a *safe mode*.

## Kano Splash

`kano-splash` is a tool to show very fast popup messages based on image bitmaps.
It uses the RaspberryPI GPU directly so it's very fast, and it sits on top of all desktop apps.

## kano-launcher

Launches KanoOS project apps, and allows for an organized termination afterwars.

## Kano Toolset Python bindings

The `kano` directory contains a lot of useful functions to do small tasks on the OS.
It is used widely across all Kano apps. They can be easily imported 
from python e.g. ```from kano.utils import get_rpi_model; print get_rpi_model()```

The `gtk3` subdirectory contains a collection of UI widgets with a uniform Kano look & feel.
Gtk styles used across these are located under the `media` directory.

## Network startup script

`kano.script` under `udhcpc` is a script that is invoked to support the DHCP network connections.
It sets up the IP address, DNS servers, and default route.

It also provides a hook script which is called when DHCP events occur, for example when
obtaining a lease: `bin/kano-network-hook`. This hook script is used to send the CPU ID 
and model name to Kano for usage statistics.

## uinput

This tool allows for sending keyboard events into the system, as if they were pressed by the user.
It is currently not stable and is not used or packaged into KanoOS.

## iospeed

The script is a handy set of steps to compute your SD Card Input/Output throughput.

## kano-shutdown

Script to shutdown the system after a confirmation message on the graphic frontend.
The user needs sudo NOPASSWD: privileges for /sbin/poweroff.

## webapp

A webkit based browser is provided under `kano/wepapp`. This component is used from
all Kano Blocks apps, mainly Make Pong and Make Minecraft to provide the user interaction panel.

The Javascript module `js/backend-api.js` is used as a hack in wepapp to provide for
download callbacks necessary to download content from Kano World.
