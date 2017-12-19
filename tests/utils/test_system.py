#
# test_system.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the kano.utils.system module
#

import pytest


DEBIAN_VERSION_FILE = '/etc/debian_version'
INIT_FILE = '/sbin/init'
SYSTEMD_INIT_FILE = '/lib/systemd/systemd'


@pytest.mark.parametrize(
    'version,expected',
    [
        ('8.0', True),
        ('7.0', False),
        ('9.0', False),
        ('8.1', True),
        ('8.39020', True),
        ('88.0', False),
        ('', False),
        ('not a version', False),
        ('not.a.version', False),
        ('8.something', True),
        ('major.version.84', False),
    ]
)
def test_is_jessie(fs, version, expected):
    from kano.utils.system import is_jessie

    fs.CreateFile(DEBIAN_VERSION_FILE, contents=version)

    assert is_jessie() == expected


def test_is_jessie_no_file(fs):
    from kano.utils.system import is_jessie

    assert not is_jessie()


def test_is_systemd(fs):
    from kano.utils.system import is_systemd

    fs.CreateFile(SYSTEMD_INIT_FILE)
    fs.CreateLink(INIT_FILE, SYSTEMD_INIT_FILE)

    assert is_systemd()


def test_is_systemd_no_link(fs):
    from kano.utils.system import is_systemd

    fs.CreateFile(INIT_FILE)

    assert not is_systemd()


def test_is_systemd_wrong_link(fs):
    from kano.utils.system import is_systemd

    fs.CreateFile(SYSTEMD_INIT_FILE)
    fs.CreateLink(INIT_FILE, '/some/wrong/file')

    assert not is_systemd()


def test_is_systemd_missing_link(fs):
    from kano.utils.system import is_systemd

    assert not is_systemd()
