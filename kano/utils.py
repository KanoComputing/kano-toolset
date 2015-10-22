#!/usr/bin/env python

# kano.utils
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

'''
'''

import os
import re
import subprocess
import sys
import signal
import shutil
import datetime
import getpass
import pwd
import grp
import json


def run_cmd(cmd, localised=False, unsudo=False):
    '''
    Executes cmd, returning stdout, stderr, return code
    if localised is False, LC_ALL will be set to "C"
    '''
    env = os.environ.copy()
    if not localised:
        env['LC_ALL'] = 'C'

    if unsudo and 'SUDO_USER' in os.environ and os.environ['SUDO_USER'] != 'root':
        cmd = "sudo -u {} bash -c '{}' ".format(os.environ['SUDO_USER'], cmd)

    process = subprocess.Popen(cmd, shell=True, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               preexec_fn=restore_signals)

    stdout, stderr = process.communicate()
    returncode = process.returncode
    return stdout, stderr, returncode


def run_cmd_log(cmd, localised=False, unsudo=False):
    '''
    Wrapper against run_cmd but Kano Logging executuion and return code
    '''

    from kano.logging import logger

    out, err, rv = run_cmd(cmd, localised, unsudo)
    logger.info("Command: {}".format(cmd))

    if len(out.strip()) > 0:
        logger.info(out)

    if len(err.strip()) > 0:
        logger.error(err)

    logger.info("Return value: {}".format(rv))

    return out, err, rv


def run_bg(cmd, localised=False, unsudo=False):
    '''
    Starts cmd program in the background
    '''
    env = os.environ.copy()
    if not localised:
        env['LC_ALL'] = 'C'

    if unsudo and 'SUDO_USER' in os.environ and os.environ['SUDO_USER'] != 'root':
        cmd = "sudo -u {} bash -c '{}' ".format(os.environ['SUDO_USER'], cmd)

    s=subprocess.Popen(cmd, shell=True, env=env)
    return s


def run_term_on_error(cmd, localised=False):
    o, e, rc = run_cmd(cmd, localised)
    if e:
        sys.exit('\nCommand:\n{}\n\nterminated with error:\n{}'.format(cmd, e.strip()))
    return o, e, rc


def run_print_output_error(cmd, localised=False):
    o, e, rc = run_cmd(cmd, localised)
    if o or e:
        print '\ncommand: {}'.format(cmd)
    if o:
        print 'output:\n{}'.format(o.strip())
    if e:
        print '\nerror:\n{}'.format(e.strip())
    return o, e, rc


def is_gui():
    return 'DISPLAY' in os.environ


def read_file_contents(path):
    if os.path.exists(path):
        with open(path) as infile:
            return infile.read().strip()


def write_file_contents(path, data):
    with open(path, 'w') as outfile:
        outfile.write(data)


def read_file_contents_as_lines(path):
    if os.path.exists(path):
        with open(path) as infile:
            content = infile.readlines()
            lines = [line.strip() for line in content]
            return lines


def delete_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)


def delete_file(file):
    if os.path.exists(file):
        os.remove(file)


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


def get_date_now():
    return datetime.datetime.utcnow().isoformat()


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_user_getpass():
    return getpass.getuser()


def get_user():
    return os.environ['LOGNAME']


def get_user_unsudoed():
    if 'SUDO_USER' in os.environ:
        return os.environ['SUDO_USER']
    elif 'LOGNAME' in os.environ:
        return os.environ['LOGNAME']
    else:
        return 'root'


def get_home():
    return os.path.expanduser('~')


def get_home_by_username(username):
    return pwd.getpwnam(username).pw_dir


def get_cpu_id():
    '''
    Returns the RaspberryPI Serial number from /proc/cpuinfo
    '''
    cpuinfo_file = '/proc/cpuinfo'
    lines = read_file_contents_as_lines(cpuinfo_file)
    if not lines:
        return

    for l in lines:
        parts = [p.strip() for p in l.split(':')]
        if parts[0] == 'Serial':
            return parts[1].upper()


def get_mac_address():
    cmd = '/sbin/ifconfig -a eth0 | grep HWaddr'
    o, _, _ = run_cmd(cmd)
    if len(o.split('HWaddr')) != 2:
        return
    mac_addr = o.split('HWaddr')[1].strip()
    mac_addr_str = mac_addr.upper()
    if len(mac_addr_str) == 17:
        return mac_addr_str


def read_json(filepath, silent=True):
    try:
        return json.loads(read_file_contents(filepath))
    except Exception:
        if not silent:
            raise


def write_json(filepath, data, prettyprint=False, sort_keys=True):
    with open(filepath, 'w') as outfile:
        json.dump(data, outfile, indent=2, sort_keys=sort_keys)
    if prettyprint:
        _, _, rc = run_cmd('which underscore')
        if rc == 0:
            cmd = 'underscore print -i {filepath} -o {filepath}'.format(filepath=filepath)
            run_cmd(cmd)


def is_number(str):
    try:
        float(str)
        return True
    except (ValueError, TypeError):
        return False


def uniqify_list(seq):
    # Order preserving
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def download_url(url, file_path):
    import requests
    try:
        with open(file_path, 'wb') as handle:
            request = requests.get(url, stream=True, proxies=proxies)
            if not request.ok:
                return False, request.text
            for block in request.iter_content(1024):
                if not block:
                    break
                handle.write(block)
        return True, None
    except Exception as e:
        return False, str(e)


def requests_get_json(url, params=None):
    import requests
    try:
        r = requests.get(url, params=params, proxies=proxies)
        if r.ok:
            return r.ok, None, r.json()
        else:
            return r.ok, r.text, None
    except Exception as e:
        return False, str(e), None


def is_installed(program):
    '''
    Returns True if "program" is recognized as an executable command in PATH
    '''
    _, _, rc = run_cmd('which {}'.format(program))
    return rc == 0


def list_dir(dir):
    if os.path.exists(dir):
        return os.listdir(dir)
    return list()


def chown_path(path, user=None, group=None):
    user_unsudoed = get_user_unsudoed()
    if not user:
        user = user_unsudoed
    if not group:
        group = user_unsudoed
    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid
        os.chown(path, uid, gid)
    except KeyError as e:
        from kano.logging import logger
        logger.error(
            'user {} or group {} do not match with existing'.format(user, group))
        ret_val = False
    except OSError as e:
        from kano.logging import logger
        logger.error(
            'Error while trying to chown, root priviledges needed {}'.format(e))
        ret_val = False
    else:
        ret_val = True
    return ret_val


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
        _, _, rc = run_cmd_log(cmd)

    return rc == 0


def is_running(program):
    cmd = "pgrep -f '{}' -l | grep -v pgrep | wc -l".format(program)
    o, _, _ = run_cmd(cmd)
    return int(o)


def enforce_root(msg):
    if os.getuid() != 0:
        sys.stderr.write(msg + "\n")
        sys.exit(1)


def detect_kano_keyboard():

    # Get information of all devices
    o, _, _ = run_cmd('lsusb -v')

    # Kano keyboard has the following information:
    # Vendor id:  0x1997
    # Product id: 0x2433
    try:
        o.index('1997')
        o.index('2433')
    except:
        return False

    return True


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
    millibel = 400

    cmd = "amixer | grep %"
    o, _, _ = run_cmd(cmd)
    o = o.strip().split(' ')

    try:
        millibel = int(o[2])
    except Exception:
        msg = 'asmixer format bad for millibel, o: {}'.format(o)
        logger.error(msg)
        pass

    try:
        percent = int(o[3].translate(None, '[]%'))
    except Exception:
        msg = 'asmixer format bad for percent, o: {}'.format(o)
        logger.error(msg)
        pass

    # logger.debug('percent: {}, millibel: {}'.format(percent, millibel))

    return percent, millibel


def is_model_a(revision=None):
    return get_rpi_model(revision) == 'RPI/A'


def is_model_b(revision=None):
    return get_rpi_model(revision) == 'RPI/B'


def is_model_b_plus(revision=None):
    return get_rpi_model(revision) == 'RPI/B+'


def is_model_2_b(revision=None):
    return get_rpi_model(revision) == 'RPI/2/B'


def get_rpi_model(revision=None):
    '''
    Returns a string identifying the RaspberryPI model (RPI A/B/B+/2B)

    Source for RaspberrPI model numbers documented at:
    http://elinux.org/RPi_HardwareHistory
    '''
    try:
        model_name=overclocked=''

        if not revision:
            o, _, _ = run_cmd('cat {}'.format('/proc/cpuinfo'))
            o = o.splitlines()
            for entry in o:
                if entry.startswith('Revision'):
                    revision=entry.split(':')[1]

        if revision == 'Beta':
            model_name='RPI/B (Beta)'
        elif int(revision, 16)  & 0x00ff in (0x2, 0x3, 0x4, 0x5, 0x6, 0xd, 0xe, 0xf):
            model_name='RPI/B'
        elif int(revision, 16) & 0x00ff in (0x7, 0x8, 0x9):
            model_name='RPI/A'
        elif int(revision, 16) & 0x00ff == 0x10:
            model_name='RPI/B+'
        elif int(revision,16) & 0x00ff == 0x11:
            model_name='Compute Module'
        elif int(revision,16) & 0x00ff == 0x12:
            model_name='RPI/A+'
        elif int(revision,16) & 0x00FFFFFF >= 0x00A01041:
            model_name='RPI/2/B'
        else:
            model_name='unknown revision: {}'.format(revision)

        return '{} {}'.format(model_name, overclocked).strip()

    except:
        return 'Error getting model name'


def is_monitor():
    status_str, _, _ = run_cmd('/usr/bin/tvservice -s')
    return 'RGB full' in status_str


def get_program_name():
    return os.path.basename(sys.argv[0])


def debug_requests():
    import httplib

    old_send = httplib.HTTPConnection.send

    def new_send(self, data):
        print data
        return old_send(self, data)
    httplib.HTTPConnection.send = new_send


def pkill(clues):
    if type(clues) == str:
        clues = [clues]

    psx, _, _ = run_cmd("ps x")
    for line in psx.split("\n"):
        for clue in clues:
            if clue in line:
                pid = line.split()[0]
                run_cmd("kill {}".format(pid))


def get_all_home_folders(root=False, skel=False):
    home = '/home'
    folders = [os.path.join(home, f) for f in os.listdir(home)]
    if root:
        folders += ['/root']
    if skel:
        folders += ['/etc/skel']
    return folders


try:
    from kano_settings.system.proxy import get_requests_proxies
    proxies = get_requests_proxies()
except Exception:
    proxies = None


def sed(pattern, replacement, file_path, use_regexp=True):
    """ Search and replace a pattern in a file.

    The search happens line-by-line, multiline patterns won't work

    :param pattern: a regular expression to search for
    :param replacement: the replacement string
    :param file_path: location of the file to process
    :returns: number of lines changed
    :raises IOError: File doesn't exist
    """

    changed = 0

    with open(file_path, "r") as file_handle:
        lines = file_handle.readlines()

    with open(file_path, "w") as file_handle:
        for line in lines:
            if use_regexp:
                modified_line = re.sub(pattern, replacement, line)
            else:
                modified_line = line.replace(pattern, replacement)

            file_handle.write(modified_line)

            if line != modified_line:
                changed += 1

    return changed


def get_free_space(path="/"):
    """
        Returns the amount of free space in certain location in MB

        :param path: The location to measure the free space at.
        :type path: str

        :return: Number of free megabytes.
        :rtype: int
    """

    out, err, rv = run_cmd("df {}".format(path))

    device, size, used, free, percent, mp = out.split('\n')[1].split()

    return int(free) / 1024


class open_locked(file):
    """ A version of open with an exclusive lock to be used within
        controlled execution statements.
    """
    def __init__(self, *args, **kwargs):
        super(open_locked, self).__init__(*args, **kwargs)
        fcntl.flock(self, fcntl.LOCK_EX)

