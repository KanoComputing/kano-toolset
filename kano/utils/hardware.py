# hardware.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


from kano.utils.shell import run_cmd
from kano.utils.file_operations import read_file_contents_as_lines


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
        model_name = overclocked = ''

        if not revision:
            o, _, _ = run_cmd('cat {}'.format('/proc/cpuinfo'))
            o = o.splitlines()
            for entry in o:
                if entry.startswith('Revision'):
                    revision = entry.split(':')[1]

        if revision == 'Beta':
            model_name = 'RPI/B (Beta)'
        elif int(revision, 16)  & 0x00ff in (0x2, 0x3, 0x4, 0x5, 0x6, 0xd, 0xe, 0xf):
            model_name = 'RPI/B'
        elif int(revision, 16) & 0x00ff in (0x7, 0x8, 0x9):
            model_name = 'RPI/A'
        elif int(revision, 16) & 0x00ff == 0x10:
            model_name = 'RPI/B+'
        elif int(revision, 16) & 0x00ff == 0x11:
            model_name = 'Compute Module'
        elif int(revision, 16) & 0x00ff == 0x12:
            model_name = 'RPI/A+'
        elif int(revision, 16) & 0x00FFFFFF >= 0x00A01041:
            model_name = 'RPI/2/B'
        else:
            model_name = 'unknown revision: {}'.format(revision)

        return '{} {}'.format(model_name, overclocked).strip()

    except:
        return 'Error getting model name'


def is_monitor():
    status_str, _, _ = run_cmd('/usr/bin/tvservice -s')
    return 'RGB full' in status_str


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
