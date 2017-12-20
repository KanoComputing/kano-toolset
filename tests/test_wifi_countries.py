#!/usr/bin/python
#
# test_wifi_countries.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This module tests Wireless support for country codes
#


import os
import textwrap
import subprocess
import pytest


TEST_NETWORK = {
    'essid': 'testessid',
    'psk': 'testpassphrase',
    'wpa_passphrase': textwrap.dedent('''
        network={
                ssid="testessid"
                #psk="testpassphrase"
                psk=5a27f391c26458ddb9be0c347291a0ee1f419c41be9e48091cf0bc4e59b00813
        }
    ''').lstrip()
}
TEST_ESSID = 'testessid'
TEST_CONFFILE = '/tmp/test_wifi_countries.conf'



@pytest.fixture(scope='function')
def get_wpa_conf(monkeypatch, fs):
    monkeypatch.setenv('KANO_WIFI_COUNTRY', '')
    monkeypatch.setenv('LANG', '')

    def fake_subprocess_check_output(cmd):
        if type(cmd) != list:
            return

        if cmd[0] == 'wpa_passphrase':
            return TEST_NETWORK.get('wpa_passphrase')


    def get_conf():
        if not os.path.exists(TEST_CONFFILE):
            return None

        with open(TEST_CONFFILE) as conf_f:
            conf = conf_f.readlines()

        for line in conf:
            if line.find('country=') != -1:
                return line[line.find('country=') + 8:].strip()

        return None

    monkeypatch.setattr(
        subprocess, 'check_output',
        fake_subprocess_check_output
    )

    conf_dir = os.path.dirname(TEST_CONFFILE)
    if not fs.Exists(conf_dir):
        fs.CreateDirectory(conf_dir)

    return get_conf



def test_country_lang_argentina(monkeypatch, get_wpa_conf):
    '''
    Mimic automatic detection for Argentinian locale
    '''

    monkeypatch.setenv('LANG', 'es_AR.UTF-8')

    from kano import network
    assert network.wpa_conf(
        TEST_NETWORK.get('essid'),
        TEST_NETWORK.get('psk'),
        TEST_CONFFILE
    )

    assert get_wpa_conf() == 'AR'


def test_country_lang_spanish(monkeypatch, get_wpa_conf):
    '''
    Mimic automatic detection for Spanish locale
    '''

    monkeypatch.setenv('LANG', 'es_ES.UTF-8')

    from kano import network
    assert network.wpa_conf(
        TEST_NETWORK.get('essid'),
        TEST_NETWORK.get('psk'),
        TEST_CONFFILE
    )

    assert get_wpa_conf() == 'ES'


def test_country_custom(monkeypatch, get_wpa_conf):
    '''
    Custom country code must override LANG automatic detection
    '''

    monkeypatch.setenv('LANG', 'en_US.UTF-8')
    monkeypatch.setenv('KANO_WIFI_COUNTRY', 'es_ES.UTF-8')

    from kano import network
    assert network.wpa_conf(
        TEST_NETWORK.get('essid'),
        TEST_NETWORK.get('psk'),
        TEST_CONFFILE
    )

    assert get_wpa_conf() == 'ES'


def test_country_custom_malformed(monkeypatch, get_wpa_conf):
    '''
    Invalid format should not set any country
    '''

    monkeypatch.setenv('KANO_WIFI_COUNTRY', 'ez-ZZ-NOT-GOOD')

    from kano import network
    assert network.wpa_conf(
        TEST_NETWORK.get('essid'),
        TEST_NETWORK.get('psk'),
        TEST_CONFFILE
    )

    assert get_wpa_conf() is None


def test_country_lang_us(monkeypatch, get_wpa_conf):
    '''
    For US lang, we do not enforce wireless country code
    '''

    monkeypatch.setenv('LANG', 'en_US.UTF-8')

    from kano import network
    assert network.wpa_conf(
        TEST_NETWORK.get('essid'),
        TEST_NETWORK.get('psk'),
        TEST_CONFFILE
    )

    assert get_wpa_conf() != 'US'
