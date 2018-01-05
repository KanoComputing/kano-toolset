/**
 * hotkeys.h
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
 *
 * Functions to handle detection of hotkey presses
 *
 */


#ifndef __HOTKEYS_H__
#define __HOTKEYS_H__

#include "hid.h"


typedef enum hotkey {
    NO_HOTKEY = -1,
    CTRL_ALT = 1,
    CTRL_ALT_1,
    CTRL_ALT_7
} Hotkey;


#ifdef __cplusplus
extern "C"
Hotkey get_pressed_hotkeys(HID_HANDLE hid, bool verbose);
#endif

#ifdef __cplusplus
extern "C"
void print_hotkey(Hotkey keys);
#endif


#endif  // __HOTKEYS_H__
