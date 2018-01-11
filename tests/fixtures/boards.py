#
# boards.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for board info
#


import pytest


class BoardData(object):
    '''
    Values taken from kano.utils.hardware so that we avoid having to import the
    module in the fixture
    '''
    RPI_A_KEY = 'RPI/A'
    RPI_A_PLUS_KEY = 'RPI/A+'
    RPI_B_BETA_KEY = 'RPI/B (Beta)'
    RPI_B_KEY = 'RPI/B'
    RPI_B_PLUS_KEY = 'RPI/B+'
    RPI_ZERO_KEY = 'RPI/Zero'
    RPI_COMPUTE_KEY = 'RPI/Compute'
    RPI_2_B_KEY = 'RPI/2/B'
    RPI_3_KEY = 'RPI/3'

    RPI_A_SCORE = 1000
    RPI_A_PLUS_SCORE = 1000
    RPI_B_SCORE = 2000
    RPI_B_PLUS_SCORE = 2000
    RPI_ZERO_SCORE = 3000
    RPI_COMPUTE_SCORE = 4000
    RPI_2_B_SCORE = 5000
    RPI_3_SCORE = 7000

    RPI_1_CPU_PROFILE = 'rpi_1'
    RPI_2_CPU_PROFILE = 'rpi_2'
    RPI_3_CPU_PROFILE = 'rpi_3'


class BoardProperty(object):
    def __init__(self, prop, is_valid=True):
        self.property = prop
        self.is_valid = is_valid


PROPERTIES = [
    # BoardProperty('name'),
    BoardProperty('cpu_profile'),
    BoardProperty('performance'),
    BoardProperty('arch'),
    BoardProperty('invalid_prop', False),
]


class Board(object):
    def __init__(self, key, name, profile, perf, arm_v, is_valid=True):
        self.name = name
        self.key = key
        self.cpu_profile = profile
        self.performance = perf
        self.arm_version = arm_v
        self.arch = 'armv{}'.format(arm_v)
        self.is_valid = is_valid


BOARDS = [
    Board(
        key=BoardData.RPI_A_KEY,
        name='',
        profile=BoardData.RPI_1_CPU_PROFILE,
        perf=BoardData.RPI_A_SCORE,
        arm_v=6
    ),
    Board(
        key=BoardData.RPI_A_PLUS_KEY,
        name='',
        profile=BoardData.RPI_1_CPU_PROFILE,
        perf=BoardData.RPI_A_PLUS_SCORE,
        arm_v=6
    ),
    Board(
        key=BoardData.RPI_B_BETA_KEY,
        name='',
        profile=BoardData.RPI_1_CPU_PROFILE,
        perf=BoardData.RPI_B_SCORE,
        arm_v=6
    ),
    Board(
        key=BoardData.RPI_B_KEY,
        name='',
        profile=BoardData.RPI_1_CPU_PROFILE,
        perf=BoardData.RPI_B_SCORE,
        arm_v=6
    ),
    Board(
        key=BoardData.RPI_B_PLUS_KEY,
        name='',
        profile=BoardData.RPI_1_CPU_PROFILE,
        perf=BoardData.RPI_B_PLUS_SCORE,
        arm_v=6
    ),
    Board(
        key=BoardData.RPI_ZERO_KEY,
        name='',
        profile=BoardData.RPI_1_CPU_PROFILE,
        perf=BoardData.RPI_ZERO_SCORE,
        arm_v=6
    ),
    Board(
        key=BoardData.RPI_COMPUTE_KEY,
        name='',
        profile=BoardData.RPI_1_CPU_PROFILE,
        perf=BoardData.RPI_COMPUTE_SCORE,
        arm_v=6
    ),
    Board(
        key=BoardData.RPI_2_B_KEY,
        name='',
        profile=BoardData.RPI_2_CPU_PROFILE,
        perf=BoardData.RPI_2_B_SCORE,
        arm_v=7
    ),
    Board(
        key=BoardData.RPI_3_KEY,
        name='',
        profile=BoardData.RPI_3_CPU_PROFILE,
        perf=BoardData.RPI_3_SCORE,
        arm_v=8
    ),
    Board(
        key='fake_board',
        name='',
        profile=BoardData.RPI_3_CPU_PROFILE,
        perf=BoardData.RPI_3_SCORE,
        arm_v=100,
        is_valid=False
    )
]



@pytest.fixture(scope='module', params=BOARDS)
def board(request):
    '''
    Provides a stream of RPi boards
    '''

    yield request.param



@pytest.fixture(scope='module', params=PROPERTIES)
def board_property(request):
    '''
    Provides a stream of properties that can be expected supplied by the `board`
    fixture
    '''

    yield request.param
