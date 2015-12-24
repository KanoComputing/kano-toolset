import os
import subprocess

from kano.utils.processes import restore_signals


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
