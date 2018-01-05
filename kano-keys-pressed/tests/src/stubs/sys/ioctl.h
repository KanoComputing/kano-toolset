/**
 * ioctl.h
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
 *
 * Mock implementation of the ioctl function.
 *
 */


#ifndef __STUB_IOCTL_H__
#define __STUB_IOCTL_H__


#include <inttypes.h>
#include <vector>
#include <string>

#include "fixtures/key.h"


static std::vector<Key> ioctl_keys;

typedef uint8_t buff_t[16];


/**
 * Mock ioctl implementation
 */
int ioctl(int fd, unsigned long request, buff_t *keys_buff)
{
    memset(keys_buff, 0, sizeof(buff_t));

    for (auto key : ioctl_keys) {
        (*keys_buff)[key.byte] |= key.val;
    }

    return 0;
}


#endif  // __STUB_IOCTL_H__
