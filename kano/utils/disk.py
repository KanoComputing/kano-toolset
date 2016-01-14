# disk.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


from kano.utils.shell import run_cmd


def get_free_space(path="/"):
    """
        Returns the amount of free space in certain location in MB

        :param path: The location to measure the free space at.
        :type path: str

        :return: Number of free megabytes.
        :rtype: int
    """

    out, dummy_err, dummy_rv = run_cmd("df {}".format(path))

    dummy_device, dummy_size, dummy_used, free, dummy_percent, dummy_mp = \
        out.split('\n')[1].split()

    return int(free) / 1024


def get_partition_info():
    device = '/dev/mmcblk0'

    try:
        cmd = 'lsblk -n -b {} -o SIZE'.format(device)
        stdout, dummy_stderr, returncode = run_cmd(cmd)

        if returncode != 0:
            from kano.logging import logger
            logger.warning("error running lsblk")

            return []

        lines = stdout.strip().split('\n')
        sizes = map(int, lines)

        return sizes
    except Exception:
        return []
