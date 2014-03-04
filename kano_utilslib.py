#!/usr/bin/env python

import os
import subprocess
import sys
import signal
import shutil


def run_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               preexec_fn=restore_signals)

    stdout, stderr = process.communicate()
    returncode = process.returncode
    return stdout, stderr, returncode


def run_term_on_error(cmd):
    o, e, rc = run_cmd(cmd)
    if e:
        sys.exit('\nCommand:\n{}\n\nterminated with error:\n{}'.format(cmd, e.strip()))
    return o, e, rc


def run_print_output_error(cmd):
    o, e, rc = run_cmd(cmd)
    if o or e:
        print '\ncommand: {}'.format(cmd)
    if o:
        print 'output:\n{}'.format(o.strip())
    if e:
        print '\nerror:\n{}'.format(e.strip())
    return o, e, rc


def is_internet():
    _, _, rc = run_cmd('which fping')
    if rc == 1:
        sys.exit('fping not installed, run "apt-get install fping" first')

    _, _, rc = run_cmd('/usr/bin/is_internet')
    return rc == 0


def is_gui():
    return 'DISPLAY' in os.environ


def read_file_contents(path):
    if os.path.exists(path):
        with open(path) as infile:
            return infile.read().strip()


def read_file_contents_as_lines(path):
    if os.path.exists(path):
        with open(path) as infile:
            content = infile.readlines()
            lines = [line.strip() for line in content]
            return lines


def get_dpkg_dict():
    apps_ok = dict()
    apps_other = dict()

    cmd = 'dpkg -l'
    o, _, _ = run_cmd(cmd)
    lines = o.splitlines()
    for l in lines[5:]:
        parts = l.split()
        state = parts[0]
        name = parts[1]
        version = parts[2]

        if state == 'ii':
            apps_ok[name] = version
        else:
            apps_other[name] = version

    return apps_ok, apps_other


def deletedir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)


def deletefile(file):
    if os.path.exists(file):
        os.remove(file)


def zenity_show_progress(msg):
    if is_gui():
        p = subprocess.Popen('yes | zenity --progress --text="{}" --pulsate --no-cancel --auto-close --title="kano-updater"'.format(msg),
                             shell=True, preexec_fn=restore_signals)
        return p.pid


def restore_signals():
        signals = ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ')
        for sig in signals:
            if hasattr(signal, sig):
                signal.signal(getattr(signal, sig), signal.SIG_DFL)


def kill_child_processes(parent_pid):
    cmd = "ps -o pid --ppid {} --noheaders".format(parent_pid)
    o, _, _ = run_cmd(cmd)
    processes = [int(p) for p in o.splitlines()]
    for process in processes:
        os.kill(process, signal.SIGTERM)
