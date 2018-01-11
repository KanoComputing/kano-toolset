#
# test_system.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the kano.utils.system module
#


DF_OUTPUT = '''
Filesystem     1K-blocks    Used Available Use% Mounted on
/dev/root        7399352 4011436   3021788  58% /
'''.lstrip()
DF_FREE_MB = 2950


LSBLK_OUTPUT = '''
7948206080
 100663808
7834959872
'''.lstrip()
LSBLK_PARTITION_INFO = [
    7948206080,
    100663808,
    7834959872,
]


def test_free_space(df):
    from kano.utils.disk import get_free_space
    assert get_free_space() == DF_FREE_MB



def test_partition_info(lsblk):
    from kano.utils.disk import get_partition_info
    assert get_partition_info() == LSBLK_PARTITION_INFO
