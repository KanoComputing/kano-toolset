#!/usr/bin/python

# test_logging.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This module tests the Kano logging module
#

import unittest
from kano import logging as klm

import os
import sys
import tempfile
import shutil
sys.path.append('../')


class TestNormaliseLevel(unittest.TestCase):

    def test_case_normalisation(self):
        ret = klm.normalise_level('INfo')
        self.assertEqual('info', ret)

        ret = klm.normalise_level('WarNing')
        self.assertEqual('warning', ret)

        ret = klm.normalise_level('DEBUG')
        self.assertEqual('debug', ret)

        ret = klm.normalise_level('ErroR')
        self.assertEqual('error', ret)

    def test_not_matching(self):
        ret = klm.normalise_level('random')
        self.assertEqual('none', ret)

    def test_aliases(self):
        for level in klm.LEVELS.keys():
            # create a list with aliases such as
            # ['d', 'de', 'deb', 'debu']
            aliases = [level[0:i] for i in xrange(1, len(level))]
            for alias in aliases:
                ret = klm.normalise_level(alias)
                self.assertEqual(level, ret)

    def test_wrong_aliases(self):
        ret = klm.normalise_level('ing')
        self.assertEqual('none', ret)


class TestForceFlush(unittest.TestCase):
    def get_new_logger_instance(self):
        self.logger = klm.Logger()
        self.logger.set_app_name(sys.argv[0])
        self.exp_log_fname = '{}.log'.format(self.logger._app_name)
        self.exp_log_fname_full = os.path.join(self.temp_dir,
                                               self.exp_log_fname)

    def setUp(self):
        os.environ[klm.LOG_ENV] = 'debug'
        os.environ[klm.OUTPUT_ENV] = 'error'

        self.temp_dir = tempfile.mkdtemp(dir='/tmp')
        klm._test_override_logs_dir(self.temp_dir)

        self.data_from_log = {}

        self.get_new_logger_instance()

        # Prepare a few messages to write
        self.msg_err_str = 'This is an error OH NO!'
        self.msg_warn_str = 'Attention warning this is a warning'
        self.msg_info_str = 'This is a piece of information'
        self.msg_debug_str = 'I have no idea what is going on'

    def tearDown(self):
        # We may want to set the env variable for force flushing, unset
        # this for the other tests
        if klm.FORCE_FLUSH_ENV in os.environ:
            os.environ.pop(klm.FORCE_FLUSH_ENV)

        # Delete the folder where our logs were put
        shutil.rmtree(self.temp_dir)
        del self.logger
        self.data_from_log.clear()

    def get_data_from_log_file(self):
        self.data_from_log = klm.read_logs()
        self.assertIn(self.exp_log_fname_full,
                      self.data_from_log,
                      msg='No log file was found for this app')

    def check_if_messages_are_in(self, msgs):
        ''' Checks if the standard messages are in the message list
        that is given in as a list() instance
        '''
        self.assertIn(self.msg_err_str,
                      msgs,
                      msg='The error message put in was not found')
        self.assertIn(self.msg_warn_str,
                      msgs,
                      msg='The warn message put in was not found')
        self.assertIn(self.msg_info_str,
                      msgs,
                      msg='The info message put in was not found')
        self.assertIn(self.msg_debug_str,
                      msgs,
                      msg='The debug message put in was not found')

    def test_regular_write(self):
        ''' Print a message for each of the levels, close the log
        file and check whether it is included in the log file
        '''
        self.logger.error(self.msg_err_str)
        self.logger.warn(self.msg_warn_str)
        self.logger.info(self.msg_info_str)
        self.logger.debug(self.msg_debug_str)
        # flush flushes and closes the file
        self.logger.flush()
        self.get_data_from_log_file()
        entries = self.data_from_log[self.exp_log_fname_full]
        msgs = [a['message'] for a in entries]
        self.check_if_messages_are_in(msgs)

    def test_force_flush_flag(self):
        ''' Print a message for each of the levels, but force flush
        it to the log file through using the force_flush flag argument
        '''
        self.logger.error(self.msg_err_str, force_flush=True)
        self.logger.warn(self.msg_warn_str, force_flush=True)
        self.logger.info(self.msg_info_str, force_flush=True)
        self.logger.debug(self.msg_debug_str, force_flush=True)
        self.get_data_from_log_file()
        entries = self.data_from_log[self.exp_log_fname_full]
        msgs = [a['message'] for a in entries]
        self.check_if_messages_are_in(msgs)

    def test_force_flush_env(self):
        ''' Print a message for each of the levels, but force flush
        it to the log file through using the force_flush env var
        '''
        os.environ[klm.FORCE_FLUSH_ENV] = '1'
        # We need to get a new instance since we changed the envs
        self.get_new_logger_instance()
        self.logger.error(self.msg_err_str)
        self.logger.warn(self.msg_warn_str)
        self.logger.info(self.msg_info_str)
        self.logger.debug(self.msg_debug_str)
        self.get_data_from_log_file()
        entries = self.data_from_log[self.exp_log_fname_full]
        msgs = [a['message'] for a in entries]
        self.check_if_messages_are_in(msgs)

    def test_force_flush_fns(self):
        ''' Print a message for each of the levels, but force flush
        it to the log file through using the force_flush class functions
        '''
        self.logger.set_force_flush()
        self.logger.error(self.msg_err_str)
        self.logger.warn(self.msg_warn_str)
        self.logger.info(self.msg_info_str)
        self.logger.debug(self.msg_debug_str)
        self.logger.unset_force_flush()
        self.get_data_from_log_file()
        entries = self.data_from_log[self.exp_log_fname_full]
        msgs = [a['message'] for a in entries]
        self.check_if_messages_are_in(msgs)

if __name__ == '__main__':
    unittest.main()
