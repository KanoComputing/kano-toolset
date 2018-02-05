# hardware.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utilities relating to RPi hardware and Kano peripherals


from kano.logging import logger
from kano.utils.shell import run_cmd
from kano.utils.file_operations import read_file_contents_as_lines


RPI_A_KEY = 'RPI/A'
RPI_A_PLUS_KEY = 'RPI/A+'
RPI_B_BETA_KEY = 'RPI/B (Beta)'
RPI_B_KEY = 'RPI/B'
RPI_B_PLUS_KEY = 'RPI/B+'
RPI_ZERO_KEY = 'RPI/Zero'
RPI_ZERO_W_KEY = 'RPI/Zero/W'
RPI_COMPUTE_KEY = 'RPI/Compute'
RPI_COMPUTE_3_KEY = 'RPI/Compute/3'
RPI_2_B_KEY = 'RPI/2/B'
RPI_3_KEY = 'RPI/3'


# "performance" scores for RPi boards
RPI_A_SCORE = 1000
RPI_A_PLUS_SCORE = 1000
RPI_B_SCORE = 2000
RPI_B_PLUS_SCORE = 2000
RPI_ZERO_SCORE = 3000
RPI_ZERO_W_SCORE = 3000
RPI_COMPUTE_SCORE = 4000
RPI_2_B_SCORE = 5000
RPI_COMPUTE_3_SCORE = 7000
RPI_3_SCORE = 7000

RPI_1_CPU_PROFILE = 'rpi_1'
RPI_2_CPU_PROFILE = 'rpi_2'
RPI_3_CPU_PROFILE = 'rpi_3'

CPUINFO_FILE = '/proc/cpuinfo'


'''
Lookup table with keys as given by get_rpi_model() containing:
    * Human readable 'name' of the board
    * 'cpu_profile' which details the settings to use
    * 'performance' scores
'''
BOARD_PROPERTIES = {
    RPI_A_KEY: {
        'name': 'Raspberry Pi A',
        'cpu_profile': RPI_1_CPU_PROFILE,
        'performance': RPI_A_SCORE,
        'arch': "armv6"
    },
    RPI_A_PLUS_KEY: {
        'name': 'Raspberry Pi A+',
        'cpu_profile': RPI_1_CPU_PROFILE,
        'performance': RPI_A_PLUS_SCORE,
        'arch': "armv6"
    },
    RPI_B_BETA_KEY: {
        'name': 'Raspberry Pi B (Beta)',
        'cpu_profile': RPI_1_CPU_PROFILE,
        'performance': RPI_B_SCORE,
        'arch': "armv6"
    },
    RPI_B_KEY: {
        'name': 'Raspberry Pi B',
        'cpu_profile': RPI_1_CPU_PROFILE,
        'performance': RPI_B_SCORE,
        'arch': "armv6"

    },
    RPI_B_PLUS_KEY: {
        'name': 'Raspberry Pi B+',
        'cpu_profile': RPI_1_CPU_PROFILE,
        'performance': RPI_B_PLUS_SCORE,
        'arch': "armv6"

    },
    RPI_ZERO_KEY: {
        'name': 'Raspberry Pi Zero',
        'cpu_profile': RPI_1_CPU_PROFILE,
        'performance': RPI_ZERO_SCORE,
        'arch': "armv6"

    },
    RPI_ZERO_W_KEY: {
        'name': 'Raspberry Pi Zero Wireless',
        'cpu_profile': RPI_1_CPU_PROFILE,
        'performance': RPI_ZERO_SCORE,
        'arch': "armv6"
    },
    RPI_COMPUTE_KEY: {
        'name': 'Raspberry Pi Compute Module',
        'cpu_profile': RPI_1_CPU_PROFILE,
        'performance': RPI_COMPUTE_SCORE,
        'arch': "armv6"
    },
    RPI_COMPUTE_3_KEY: {
        'name': 'Raspberry Pi Compute Module 3',
        'cpu_profile': RPI_3_CPU_PROFILE,
        'performance': RPI_3_SCORE,
        'arch': "armv8"
    },
    RPI_2_B_KEY: {
        'name': 'Raspberry Pi 2',
        'cpu_profile': RPI_2_CPU_PROFILE,
        'performance': RPI_2_B_SCORE,
        'arch': "armv7"
    },
    RPI_3_KEY: {
        'name': 'Raspberry Pi 3',
        'cpu_profile': RPI_3_CPU_PROFILE,
        'performance': RPI_3_SCORE,
        'arch': 'armv8'
    }
}


def get_board_property(board_key, prop):
    board = BOARD_PROPERTIES.get(board_key)

    if not board:
        return

    board_prop = board.get(prop)

    if not board_prop:
        return

    return board_prop


def detect_kano_keyboard_type():
    # Get information of all devices
    o, _, _ = run_cmd('lsusb')

    keyboard_ids = {
        'en': 'ID 1997:2433',
        'es': 'ID 1997:2434'
    }
    kano_keyboard = None
    for lang, id in keyboard_ids.iteritems():
        if id in o:
            kano_keyboard = lang
    return kano_keyboard


def detect_kano_keyboard():
    return detect_kano_keyboard_type() is not None


def is_model_a(revision=None):
    """Check if the Raspberry Pi is model 1 A"""
    return get_rpi_model(revision) == RPI_A_KEY


def is_model_a_plus(revision=None):
    """Check if the Raspberry Pi is model 1 A+"""
    return get_rpi_model(revision) == RPI_A_PLUS_KEY


def is_model_b_beta(revision=None):
    """Check if the Raspberry Pi is model 1 B beta"""
    return get_rpi_model(revision) == RPI_B_BETA_KEY


def is_model_b(revision=None):
    """Check if the Raspberry Pi is model 1 B"""
    return get_rpi_model(revision) == RPI_B_KEY


def is_model_b_plus(revision=None):
    """Check if the Raspberry Pi is model 1 B+"""
    return get_rpi_model(revision) == RPI_B_PLUS_KEY


def is_model_zero(revision=None):
    """Check if the Raspberry Pi is model Zero"""
    return get_rpi_model(revision) == RPI_ZERO_KEY


def is_model_zero_w(revision=None):
    """Check if the Raspberry Pi is model Zero Wireless"""
    return get_rpi_model(revision) == RPI_ZERO_W_KEY


def is_model_2_b(revision=None):
    """Check if the Raspberry Pi is model 2 B"""
    return get_rpi_model(revision) == RPI_2_B_KEY


def is_model_3_b(revision=None):
    """Check if the Raspberry Pi is model 3 B"""
    return get_rpi_model(revision) == RPI_3_KEY


def get_rpi_model(revision=None):
    """Get the model key of the Rasperry Pi.

    Source for Raspberry Pi model numbers documented at:
    https://www.raspberrypi.org/documentation/hardware/raspberrypi/revision-codes/README.md
    http://elinux.org/RPi_HardwareHistory

    Args:
        revision (str): Revision tag as extracted from /proc/cpuinfo.

    Returns:
        str: Model key identifying the Raspberry Pi model (RPI A/A+/B/B+/Zero/
        CM/2B/3), e.g. RPI_3_KEY
    """
    try:
        model_name = overclocked = ''

        if not revision:
            for entry in read_file_contents_as_lines(CPUINFO_FILE):
                if entry.startswith('Revision'):
                    revision = entry.split(':')[1]
                    break

        # The order of checks here is done Descending by Most Likely Model.
        if int(revision, 16) & 0x00FFFFFF in (0x00A02082, 0x00A22082, 0x00A32082):
            model_name = RPI_3_KEY

        elif int(revision, 16) & 0x00FFFFFF in (0x00A01040, 0x00A01041, 0x00A21041):
            model_name = RPI_2_B_KEY

        elif int(revision, 16) & 0x00ff in (0x10, 0x13) or \
             int(revision, 16) & 0x00FFFFFF == 0x00900032:
            model_name = RPI_B_PLUS_KEY

        elif int(revision, 16) & 0x00ff in (0x2, 0x3, 0x4, 0x5, 0x6, 0xd, 0xe, 0xf):
            model_name = RPI_B_KEY

        elif int(revision, 16) & 0x00ff in (0x12, 0x15) or \
             int(revision, 16) & 0x00FFFFFF == 0x00900021:
            model_name = RPI_A_PLUS_KEY

        elif int(revision, 16) & 0x00ff in (0x7, 0x8, 0x9):
            model_name = RPI_A_KEY

        elif int(revision, 16) & 0x00FFFFFF == 0x009000C1:
            model_name = RPI_ZERO_W_KEY

        elif int(revision, 16) & 0x00FFFFFF in (0x00900092, 0x00900093, 0x00920093):
            model_name = RPI_ZERO_KEY

        elif int(revision, 16) & 0x00FFFFFF == 0x00A020A0:
            model_name = RPI_COMPUTE_3_KEY

        elif int(revision, 16) & 0x00ff in (0x11, 0x14):
            model_name = RPI_COMPUTE_KEY

        elif revision == 'Beta':
            model_name = RPI_B_BETA_KEY

        else:
            model_name = 'unknown revision: {}'.format(revision)
            logger.error('Unknown Raspberry Pi board revision: {}'.format(revision))

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
    lines = read_file_contents_as_lines(CPUINFO_FILE)
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


def has_min_performance(score):
    """
    Check if the hardware we're running on has a minimum given performance.

    This can be used to abstract the hardware and judge whether a certain
    feature can be enabled due to its performance requriements.

    Args:
        score (int): A performance score just like the ones in PERFORMANCE_SCORES

    Returns:
        bool: True if the hardware has a higher score than the given or if the
              hardware could not be detected; and False otherwise
    """

    model = get_rpi_model()
    model_score = get_board_property(model, 'performance')

    return not model_score or model_score >= score
