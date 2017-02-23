#!/usr/bin/python

# test_wifi_countries.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This module tests Wireless support for country codes
#

import os
import sys
import unittest

sys.path.insert(0, '../')
from kano import network

test_essid='testessid'
test_passphrase='testpassphrase'
test_conffile='/tmp/test_wifi_countries.conf'

class TestWirelessCountries(unittest.TestCase):

    def setUp(self):
        self._set_envvar('KANO_WIFI_COUNTRY', '')
        self._set_envvar('LANG', '')        
    
    def _set_envvar(self, envvar, value):
        os.environ[envvar] = value

    def _generate_conf(self):
        if os.path.isfile(test_conffile):
            os.unlink(test_conffile)
        network.wpa_conf(test_essid, test_passphrase, test_conffile)

    def _get_conf(self):
        with open(test_conffile) as f:
            a=f.readlines()

        for l in a:
            if l.find('country=') != -1:
                return l[l.find('country=') + 8:].strip()

        return None

    def test_country_lang_argentina(self):
        # Mimic automatic detection for Argentinian locale
        self._set_envvar('LANG', 'es_AR.UTF-8')
        self._generate_conf()
        self.assertEqual(self._get_conf(), 'AR', msg=self._get_conf())

    def test_country_lang_spanish(self):
        # Mimic automatic detection for Spanish locale
        self._set_envvar('LANG', 'es_ES.UTF-8')
        self._generate_conf()
        self.assertEqual(self._get_conf(), 'ES', msg=self._get_conf())

    def test_country_custom(self):
        # Custom country code must override LANG automatic detection
        self._set_envvar('LANG', 'en_US.UTF-8')
        self._set_envvar('KANO_WIFI_COUNTRY', 'es_ES.UTF-8')
        self._generate_conf()
        self.assertEqual(self._get_conf(), 'ES', msg=self._get_conf())

    def test_country_custom_malformed(self):
        # Invalid format should not set any country
        self._set_envvar('KANO_WIFI_COUNTRY', 'ez-ZZ-NOT-GOOD')
        self._generate_conf()
        self.assertEqual(self._get_conf(), None, msg=self._get_conf())

    def test_country_lang_us(self):
        # For US lang, we do not enforce wireless country code
        self._set_envvar('LANG', 'en_US.UTF-8')
        self._generate_conf()
        self.assertNotEqual(self._get_conf(), 'US', msg=self._get_conf())



if __name__ == '__main__':
    unittest.main()
