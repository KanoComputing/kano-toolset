/**
 * ifaces.c
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Methods for interracting with interfaces
 */

#include <ifaddrs.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#include "kano/networking/ifaces.h"

/**
 * Search through the available interfaces and return the first available
 * which matches the type provided
 *
 * The caller is responsible for freeing iface_name
 *
 * Upon error, iface_name does not need freeing
 */
int select_iface(const char *iface_type, char **iface_name)
{
    struct ifaddrs *iface_addr;

    if (getifaddrs(&iface_addr) == -1)
        return E_NO_INTERFACES;

    struct ifaddrs *candidate_iface = iface_addr;
    bool match = false;

    while (candidate_iface != NULL && !match) {
        if (strstr(candidate_iface->ifa_name, iface_type) != NULL) {
            match = true;
            break;
        }

        candidate_iface = candidate_iface->ifa_next;
    }

    if (!match) {
        freeifaddrs(iface_addr);
        return E_NO_INTERFACES;
    }

    *iface_name = strdup(candidate_iface->ifa_name);
    freeifaddrs(iface_addr);

    return 0;
}

/**
 * Check for interfaces of the provided type and print the interface name
 */
int check_iface_type(const char *iface_type)
{
    char *iface;

    if (select_iface(iface_type, &iface) == E_NO_INTERFACES) {
        printf("No interfaces for iface type %s\n", iface_type);
        return E_NO_INTERFACES;
    }

    printf("Found %s iface: %s\n", iface_type, iface);
    free(iface);

    return 0;
}
