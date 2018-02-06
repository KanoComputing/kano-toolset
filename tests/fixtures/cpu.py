#
# cpu.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for fake /proc/cpuinfo files
#


import os
import json
import pytest

from tests.fixtures.boards import BoardData


CPUINFO_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'cpuinfo'
)
# TODO: Add configurations for other RPi devices
PLATFORMS = [
    ('rpi_3', BoardData.RPI_3_KEY),
    ('rpi_2', BoardData.RPI_2_B_KEY),
    ('empty', None),
    ('incorrect', None),
    ('garbage', None)
]


@pytest.fixture(scope='function', params=PLATFORMS)
def cpu(request, fs):
    '''
    Simulates several different platforms, each having a CPU of a different
    underlying architectures. It does this by mocking the system outputs which
    would be associated with such a CPU, it does not actually emulate the
    instruction set.
    '''

    platform, key = request.param

    cpuinfo_json_path = os.path.join(
        CPUINFO_DIR,
        '{}_cpuinfo.json'.format(platform)
    )
    fs.add_real_file(cpuinfo_json_path)
    with open(cpuinfo_json_path, 'r') as cpuinfo_json_f:
        cpuinfo_json = json.load(cpuinfo_json_f)

    cpuinfo_dump_path = os.path.join(
        CPUINFO_DIR,
        '{}_cpuinfo.dump'.format(platform)
    )
    cpu_file = fs.add_real_file(cpuinfo_dump_path)
    fs.CreateLink('/proc/cpuinfo', cpuinfo_dump_path)

    cpu_file.platform = platform
    cpu_file.platform_key = key
    cpu_file.serial = cpuinfo_json.get('serial', None)
    cpu_file.revision = cpuinfo_json.get('revision', None)

    if cpu_file.serial == '':
        cpu_file.serial = None

    return cpu_file
