# gui.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import os
import subprocess

from kano.utils.shell import restore_signals


def is_gui():
    return 'DISPLAY' in os.environ


def zenity_show_progress(msg, title=None):
    if title is None:
        title = ''
    if is_gui():
        cmd = 'yes | zenity --progress --text="{}" --pulsate --no-cancel ' + \
              '--auto-close --title="{}"'
        p = subprocess.Popen(
            cmd.format(msg, title),
            shell=True,
            preexec_fn=restore_signals
        )
        return p.pid
