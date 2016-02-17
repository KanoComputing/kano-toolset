# dbus_interface.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# DBus helper functions
#

import dbus


def get_all_properties(bus_proxy, interface):
    properties_iface = dbus.Interface(
        bus_proxy, 'org.freedesktop.DBus.Properties'
    )

    return {
        unicode(key): unicode(value)
        for key, value in properties_iface.GetAll(interface).iteritems()
    }


def get_property(bus_proxy, interface, prop):
    properties_iface = dbus.Interface(
        bus_proxy, 'org.freedesktop.DBus.Properties'
    )

    return unicode(properties_iface.Get(interface, prop))


def set_property(bus_proxy, interface, prop, val):
    properties_iface = dbus.Interface(
        bus_proxy, 'org.freedesktop.DBus.Properties'
    )

    return properties_iface.Set(interface, prop, val)


def dbus_to_bool(val):
    return val == u'1'
