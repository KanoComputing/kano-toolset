/**
 * hotkeys.cpp
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
 *
 * Functions to handle detection of hotkey presses
 *
 */


#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <memory.h>
#include <iostream>
#include <iomanip>
#include <vector>

#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>

#include <inttypes.h>
#include <linux/input.h>

#include "hid.h"
#include "hotkeys.h"


// internal functions
bool add_keymask(uint8_t *key_mask, uint8_t sz, const uint8_t key_bit);
bool mask_match(uint8_t *ioctl_buff, uint8_t buff_sz, uint8_t *key_mask, uint8_t mask_sz);
bool are_keys_pressed(uint8_t *ioctl_buff, uint8_t buff_sz, std::vector<uint8_t> keys);
void dump_ioctl_data(uint8_t *keys, int sz);
Hotkey check_hotkeys(int udev_handle, bool verbose);


/**
 * Checks all the provided udev handles for the set of registered hotkeys
 */
Hotkey get_pressed_hotkeys(HID_HANDLE hid, bool verbose)
{
    Hotkey keys;

    if ((keys = check_hotkeys(hid->fdkbd0, verbose)) != NO_HOTKEY) {
        return keys;
    }

    if ((keys = check_hotkeys(hid->fdkbd1, verbose)) != NO_HOTKEY) {
        return keys;
    }

    if ((keys = check_hotkeys(hid->fdkbd2, verbose)) != NO_HOTKEY) {
        return keys;
    }

    return NO_HOTKEY;
}


/**
 * Appends the key (supplied as an integer describing the index of the bit to
 * raise in the the key mask) to the supplied key mask [given (often) in the
 * form of a 16 byte key mask]
 */
bool add_keymask(uint8_t *key_mask, uint8_t sz, const uint8_t key_bit)
{
    uint8_t remainder = key_bit % 8;
    uint8_t byte_idx = (key_bit - remainder) / 8;
    uint8_t value = 0x1 << remainder;

    if (byte_idx >= sz) {
        fprintf(stderr, "Key character (%d) requested exceeds ioctl size (%d)",
                byte_idx, sz);
        return false;
    }

    key_mask[byte_idx] |= value;

    return true;
}


/**
 * Determines if the supplied keys [given (often) in the form of a 16 byte key
 * mask] match the values read directly from the ioctl EVIOCGKEY request.
 */
bool mask_match(uint8_t *ioctl_buff, uint8_t buff_sz, uint8_t *key_mask, uint8_t mask_sz)
{
    if (buff_sz != mask_sz) {
        fprintf(stderr, "ioctl buffer size (%d) doesn't match mask size (%d)",
                buff_sz, mask_sz);
        return false;
    }

    for (int i = 0; i < buff_sz; i++) {
        if (ioctl_buff[i] != key_mask[i]) {
            return false;
        }
    }

    return true;
}


/**
 * Check that they supplied keys are pressed and are the only ones pressed
 */
bool are_keys_pressed(uint8_t *ioctl_buff, uint8_t buff_sz, std::vector<uint8_t> keys)
{
    uint8_t key_mask[16] = {0};

    for (const auto key : keys) {
        add_keymask(key_mask, sizeof key_mask, key);
    }

    return mask_match(ioctl_buff, buff_sz, key_mask, sizeof key_mask);
}


/*
 * Dump the key value masks returned by ioctl EVIOCGKEY
 */
void dump_ioctl_data(uint8_t *keys, int sz)
{
    std::cout << "  Index |";

    for (int i = 0; i < sz; i++) {
        printf("  %02d | ", i);
    }

    std::cout << "\n  Key   |";

    for (int i = 0; i < sz; i++) {
        printf("0x%02x | ", keys[i]);
    }

    std::cout << std::endl;
}


/**
 * Requests EVIOCGKEY from ioctl. This populates the supplied array with a giant
 * bitmask. The associated bits can be found here:
 *     https://elixir.free-electrons.com/linux/v3.1/source/include/linux/input.h#L183
 *
 * TODO: refactor this function to accept a combination of keys to expect
 *
 * This routine is based on an IOCTL documented on this article:
 * http://baruch.siach.name/blog/posts/linux_input_keys_status/
 *

 *
 * The combination of modifier keys returned by the IOCTL are as follows
 * (discovered by testing several keyboards):
 *
 *  Key name      |  keys[idx]  |   value in decimal notation
 *  ---------------------------------------------------------
 *  Left Shift    |  5          | 4d
 *  Right Shift   |  6          | 64d
 *  Left Ctrl     |  3          | 32d
 *  Right Ctrl    |  12         | 2d
 *  Fn            |  nothing    | nothing
 *  Windows       |  15         | 32d
 *  Alt Gr        |  12         | 16d (careful with Right Ctrl)
 *  Alt           |  7          | 1d
 *
 */
Hotkey check_hotkeys(int udev_handle, bool verbose)
{
    uint8_t keys[16];

    if (ioctl(udev_handle, EVIOCGKEY(sizeof keys), &keys) < 0)
        return NO_HOTKEY;

    if (verbose) {
        std::cout << "Key device id: " << udev_handle << std::endl;
        dump_ioctl_data(keys, sizeof keys);
    }

    if (are_keys_pressed(keys, sizeof keys, {KEY_LEFTCTRL, KEY_LEFTALT})
            || are_keys_pressed(keys, sizeof keys, {KEY_RIGHTCTRL, KEY_LEFTALT})) {
        return CTRL_ALT;
    } else if (are_keys_pressed(keys, sizeof keys, {KEY_LEFTCTRL, KEY_LEFTALT, KEY_1})
            || are_keys_pressed(keys, sizeof keys, {KEY_RIGHTCTRL, KEY_LEFTALT, KEY_1})) {
        return CTRL_ALT_1;
    } else if (are_keys_pressed(keys, sizeof keys, {KEY_LEFTCTRL, KEY_LEFTALT, KEY_7})
            || are_keys_pressed(keys, sizeof keys, {KEY_RIGHTCTRL, KEY_LEFTALT, KEY_7})) {
        return CTRL_ALT_7;
    }

    return NO_HOTKEY;
}


void print_hotkey(Hotkey keys)
{
    switch(keys) {
    case CTRL_ALT:
        std::cout << "CTRL + ALT pressed (" << CTRL_ALT << ")\n";
        break;
    case CTRL_ALT_1:
        std::cout << "CTRL + ALT + 1 pressed (" << CTRL_ALT_1 << ")\n";
        break;
    case CTRL_ALT_7:
        std::cout << "CTRL + ALT + 7 pressed (" << CTRL_ALT_7 << ")\n";
        break;
    case NO_HOTKEY:
    default:
        std::cout << "No hotkeys pressed (" << NO_HOTKEY << ")\n";
    }
}
