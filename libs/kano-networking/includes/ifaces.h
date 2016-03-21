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

#include <ifaddrs.h>

enum ERRORS {
    E_NO_INTERFACES = -1,
    E_ALLOCATION_ERROR = -2
};

int sockaddr_cpy(struct sockaddr **const dest, const struct sockaddr *src);
int ifaddrs_cpy(struct ifaddrs **const dest, const struct ifaddrs *src);
int get_iface(const char *iface_type, struct ifaddrs **iface);
int select_iface(const char *iface_type, char **iface_name);
int check_iface_type(const char *iface_type);

#endif
