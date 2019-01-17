# ifaces.py
#
# Copyright (C) 2016-2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module to interface with the ifaces module of the libkano_networking library
#

import os
import ctypes

NETWORKING_LIB = 'libkano_networking.so'

try:
    LIB = ctypes.CDLL(NETWORKING_LIB)
except OSError:
    LIB = ctypes.CDLL(os.path.join(os.path.dirname(__file__), NETWORKING_LIB))


def get_iface(iface_type_str):
    iface_type = ctypes.create_string_buffer(iface_type_str)

    str_p = ctypes.c_char_p()
    pt = ctypes.pointer(str_p)

    if LIB.select_iface(iface_type, pt) != 0:
        return False

    return ctypes.string_at(str_p)


def get_wlan_device():
    return get_iface('wlan')


def get_eth_device():
    return get_iface('eth')
