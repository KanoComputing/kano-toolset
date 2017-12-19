#
# system.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for system functions
#


import sys
import pytest


@pytest.fixture(scope='function')
def fake_sys_exit(monkeypatch):
    '''
    Overrides the sys.exit() funciton to prevent termination and to keep track
    of whether it was called.
    '''

    class ExitState(object):
        quit = False
        exit_code = 0

    exit_state = ExitState()

    def fake_quit(exit_code=0):
        exit_state.quit = True
        exit_state.exit_code = exit_code

    monkeypatch.setattr(
        sys, 'exit', fake_quit
    )

    return exit_state
