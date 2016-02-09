/**
 * ifaces.h
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Methods for interracting with interfaces
 */

#ifndef __KANO_NETWORKING_IFACES__
#define __KANO_NETWORKING_IFACES__

enum ERRORS {
    E_NO_INTERFACES = -1
};

int select_iface(char * iface_type, char **iface_name);
int check_iface_type(char * iface_type);

#endif
