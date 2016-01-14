# audio.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import os

from kano.utils.shell import run_cmd, run_bg, run_cmd_log


def play_sound(audio_file, background=False):
    from kano.logging import logger

    # Check if file exists
    if not os.path.isfile(audio_file):
        logger.error('audio file not found: {}'.format(audio_file))
        return False

    _, extension = os.path.splitext(audio_file)

    if extension in ['.wav', '.voc', '.raw', '.au']:
        cmd = 'aplay -q {}'.format(audio_file)
    else:
        volume_percent, _ = get_volume()
        volume_str = '--vol {}'.format(
            percent_to_millibel(volume_percent, raspberry_mod=True))
        cmd = 'omxplayer -o both {volume} {link}'.format(
            volume=volume_str, link=audio_file)

    logger.debug('cmd: {}'.format(cmd))

    if background:
        run_bg(cmd)
        rc = 0
    else:
        dummy, dummy, rc = run_cmd_log(cmd)

    return rc == 0


def percent_to_millibel(percent, raspberry_mod=False):
    if not raspberry_mod:
        from math import log10

        multiplier = 2.5

        percent *= multiplier
        percent = min(percent, 100. * multiplier)
        percent = max(percent, 0.000001)

        millibel = 1000 * log10(percent / 100.)

    else:
        # special case for mute
        if percent == 0:
            return -11000

        min_allowed = -4000
        max_allowed = 400
        percent = percent / 100.
        millibel = min_allowed + (max_allowed - min_allowed) * percent

    return int(millibel)


def get_volume():
    from kano.logging import logger

    percent = 100

    cmd = "amixer | head -n 6 | grep -Po '(\d{1,3})(?=%)'"
    output, _, _ = run_cmd(cmd)

    try:
        percent = int(output)
    except Exception:
        msg = 'amixer format bad for percent, output: {}'.format(output)
        logger.error(msg)
        pass

    return percent
