# processes.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import os
import sys
import signal

from kano.utils.shell import run_cmd


def kill_child_processes(parent_pid):
    cmd = "ps -o pid --ppid {} --noheaders".format(parent_pid)
    o, _, _ = run_cmd(cmd)
    processes = [int(p) for p in o.splitlines()]
    for process in processes:
        os.kill(process, signal.SIGTERM)


def is_running(program):
    '''
    Returns True if at least one instance of program name is running.
    program will search through the command line, so asking for
    "connect" will return True for the process
    "wpa_supplicant -c/etc/connect.conf"
    '''
    # Search using a regex, to exclude itself (pgrep) from the list
    cmd = "pgrep -fc '[{}]{}'".format(program[0], program[1:])
    running = 0
    try:
        result = os.popen(cmd)
        running = int(result.read().strip())
    except Exception:
        pass

    return running > 0


def get_program_name():
    return os.path.basename(sys.argv[0])


def pkill(clues):
    if type(clues) == str:
        clues = [clues]

    psx, _, _ = run_cmd("ps x")
    for line in psx.split("\n"):
        for clue in clues:
            if clue in line:
                pid = line.split()[0]
                run_cmd("kill {}".format(pid))
