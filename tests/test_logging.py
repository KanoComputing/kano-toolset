#!/usr/bin/python

# test_logging.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This module tests the Kano logging module
#


import os
import sys
import contextlib
import tempfile
import shutil
import unittest
import pytest


class TestNormaliseLevel(unittest.TestCase):

    def test_case_normalisation(self):
        from kano import logging as klm

        ret = klm.normalise_level('INfo')
        self.assertEqual('info', ret)

        ret = klm.normalise_level('WarNing')
        self.assertEqual('warning', ret)

        ret = klm.normalise_level('DEBUG')
        self.assertEqual('debug', ret)

        ret = klm.normalise_level('ErroR')
        self.assertEqual('error', ret)

    def test_not_matching(self):
        from kano import logging as klm

        ret = klm.normalise_level('random')
        self.assertEqual('none', ret)

    def test_aliases(self):
        from kano import logging as klm

        for level in klm.LEVELS.keys():
            # create a list with aliases such as
            # ['d', 'de', 'deb', 'debu']
            aliases = [level[0:i] for i in xrange(1, len(level))]
            for alias in aliases:
                ret = klm.normalise_level(alias)
                self.assertEqual(level, ret)

    def test_wrong_aliases(self):
        from kano import logging as klm

        ret = klm.normalise_level('ing')
        self.assertEqual('none', ret)


@pytest.fixture(scope='function')
def new_logger(monkeypatch):
    '''
    Provides a function to get a new logger object at will, initialised with
    the desired log and output levels.

    Usage:
        def test_something(new_logger):
            with new_logger() as logger:
                assert logger is not None
    '''

    @contextlib.contextmanager
    def logger_generator(log_level='debug', output_level='error'):
        '''
        Returns the logger object itself for testing
        '''

        import kano

        # Patch the environment with the given log level
        monkeypatch.setenv(kano.logging.LOG_ENV, log_level)
        monkeypatch.setenv(kano.logging.OUTPUT_ENV, output_level)

        # Initialise the logger after setting the environment variables
        logger = kano.logging.Logger()
        logger.set_app_name(sys.argv[0])

        temp_dir = tempfile.mkdtemp()

        log_file = '{}.log'.format(logger._app_name)
        logger.log_file_path = os.path.join(
            temp_dir, log_file
        )

        # The kano.logging module is lazy loaded using kano._logging so that is
        # The module that needs patching
        monkeypatch.setattr(kano._logging, 'SYSTEM_LOGS_DIR', temp_dir)
        monkeypatch.setattr(kano._logging, 'USER_LOGS_DIR', temp_dir)

        # Prepare a few messages to write
        logger.msg_err_str = 'This is an error OH NO!'
        logger.msg_warn_str = 'Attention warning this is a warning'
        logger.msg_info_str = 'This is a piece of information'
        logger.msg_debug_str = 'I have no idea what is going on'

        def read_log_file():
            '''
            Helper for reading the log file associated with this test
            '''

            logs = kano.logging.read_logs()
            print logs
            assert logger.log_file_path in logs, \
                'No log file was found for this app'

            return logs[logger.log_file_path]

        logger.read_log_file = read_log_file

        def check_if_messages_are_in(msgs):
            '''
            Checks if the standard messages are in the message list
            that is given in as a list() instance
            '''

            assert logger.msg_err_str in msgs, \
                'The error message put in was not found'
            assert logger.msg_warn_str in msgs, \
                'The warn message put in was not found'
            assert logger.msg_info_str in msgs, \
                'The info message put in was not found'
            assert logger.msg_debug_str in msgs, \
                'The debug message put in was not found'

        logger.check_if_messages_are_in = check_if_messages_are_in

        yield logger

        shutil.rmtree(temp_dir)

    return logger_generator


def test_regular_write(new_logger):
    ''' Print a message for each of the levels, close the log
    file and check whether it is included in the log file
    '''

    with new_logger() as logger:
        logger.error(logger.msg_err_str)
        logger.warn(logger.msg_warn_str)
        logger.info(logger.msg_info_str)
        logger.debug(logger.msg_debug_str)

        # flush flushes and closes the file
        logger.flush()

        entries = logger.read_log_file()

        msgs = [a['message'] for a in entries]
        logger.check_if_messages_are_in(msgs)


def test_force_flush_flag(new_logger):
    ''' Print a message for each of the levels, but force flush
    it to the log file through using the force_flush flag argument
    '''

    with new_logger() as logger:
        logger.error(logger.msg_err_str, force_flush=True)
        logger.warn(logger.msg_warn_str, force_flush=True)
        logger.info(logger.msg_info_str, force_flush=True)
        logger.debug(logger.msg_debug_str, force_flush=True)

        entries = logger.read_log_file()

        msgs = [a['message'] for a in entries]
        logger.check_if_messages_are_in(msgs)


def test_force_flush_env(new_logger, monkeypatch):
    ''' Print a message for each of the levels, but force flush
    it to the log file through using the force_flush env var
    '''

    from kano import logging

    monkeypatch.setenv(logging.FORCE_FLUSH_ENV, '1')
    # We need to get a new instance since we changed the envs

    with new_logger() as logger:
        logger.error(logger.msg_err_str)
        logger.warn(logger.msg_warn_str)
        logger.info(logger.msg_info_str)
        logger.debug(logger.msg_debug_str)

        entries = logger.read_log_file()

        msgs = [a['message'] for a in entries]
        logger.check_if_messages_are_in(msgs)


def test_force_flush_fns(new_logger):
    ''' Print a message for each of the levels, but force flush
    it to the log file through using the force_flush class functions
    '''

    with new_logger() as logger:
        logger.set_force_flush()

        logger.error(logger.msg_err_str)
        logger.warn(logger.msg_warn_str)
        logger.info(logger.msg_info_str)
        logger.debug(logger.msg_debug_str)
        logger.unset_force_flush()

        entries = logger.read_log_file()

        msgs = [a['message'] for a in entries]
        logger.check_if_messages_are_in(msgs)
