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

#include "ifaces.h"


/**
 * Copy a 'struct sockaddr' instance
 *
 * The caller is responsible for freeing 'dest'
 */
int sockaddr_cpy(struct sockaddr **const dest, const struct sockaddr *src)
{
    if (src == NULL) {
        *dest = NULL;
        return 1;
    }

    *dest = malloc(sizeof(*src));

    if (!*dest)
        return E_ALLOCATION_ERROR;

    memcpy(*dest, src, sizeof(**dest));

    return memcmp(*dest, src, sizeof(*src)) != 0;
}


/**
 * Perform a copy of a single 'struct ifaddrs' instance
 *
 * Note: Doesn't copy the linked 'struct ifaddrs' pointed to by 'ifa_next'
 *
 * The caller is responsible for freeing 'dest' with a 'freeifaddrs()' call
 */
int ifaddrs_cpy(struct ifaddrs **const dest, const struct ifaddrs *src)
{
    struct ifaddrs *dest_if = malloc(sizeof(*src));

    if (!dest_if)
        return E_ALLOCATION_ERROR;

    // Only copy the instance so remove the linked iface
    dest_if->ifa_next = NULL;

    dest_if->ifa_name = strndup(src->ifa_name, strlen(src->ifa_name));
    dest_if->ifa_flags = src->ifa_flags;

    sockaddr_cpy(&dest_if->ifa_addr, src->ifa_addr);
    sockaddr_cpy(&dest_if->ifa_netmask, src->ifa_netmask);
    sockaddr_cpy(&dest_if->ifa_broadaddr, src->ifa_broadaddr);
    sockaddr_cpy(&dest_if->ifa_dstaddr, src->ifa_dstaddr);

    // Unsure how to handle 'void *ifa_data' - don't copy for now
    dest_if->ifa_data = NULL;

    *dest = dest_if;

    return 0;
}


/**
 * Search through the available interfaces and return the first available
 * which matches the type provided
 *
 * The caller is responsible for freeing iface
 *
 * Upon error, iface does not need freeing
 */
int get_iface(const char *iface_type, struct ifaddrs **iface)
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

    ifaddrs_cpy(iface, candidate_iface);
    freeifaddrs(iface_addr);

    return 0;
}


/**
 * Search through the available interfaces and return the name of the first
 * available which matches the type provided
 *
 * The caller is responsible for freeing iface_name
 *
 * Upon error, iface_name does not need freeing
 */
int select_iface(const char *iface_type, char **iface_name)
{
    struct ifaddrs *iface_addr;
    int rv = get_iface(iface_type, &iface_addr);

    if (rv < 0)
        return rv;

    *iface_name = strdup(iface_addr->ifa_name);
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
