//
//  hid.cpp - Human Input Device
//
//  This module encapsulates functions to deal with user keyboard and mouse activity
//  needed to decide when the screen saver needs to stop.
//

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <memory.h>

#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>

#include <inttypes.h>
#include <linux/input.h>

#include "hid.h"

// internal function
bool is_ctrl_alt_pressed(int udev_handle, bool verbose);


bool is_hotkey_pressed(HID_HANDLE hid, bool verbose)
{
    if (is_ctrl_alt_pressed(hid->fdkbd0, verbose)) {
        return true;
    }

    if (is_ctrl_alt_pressed(hid->fdkbd1, verbose)) {
        return true;
    }

    if (is_ctrl_alt_pressed(hid->fdkbd2, verbose)) {
        return true;
    }

    return false;
}

bool is_ctrl_alt_pressed(int udev_handle, bool verbose)
{
    // TODO: refactor this function to accept a combination of keys to expect
    //
    // This routine is based on an IOCTL documented on this article:
    // http://baruch.siach.name/blog/posts/linux_input_keys_status/
    //

    //
    // The combination of modifier keys returned by the IOCTL are as follows
    // (discovered by testing several keyboards):
    //
    //  Key name      |  keys[idx]  |   value in decimal notation
    //  ---------------------------------------------------------
    //  Left Shift    |  5          | 4d
    //  Right Shift   |  6          | 64d
    //  Left Ctrl     |  3          | 32d
    //  Right Ctrl    |  12         | 2d
    //  Fn            |  nothing    | nothing
    //  Windows       |  15         | 32d
    //  Alt Gr        |  12         | 16d (careful with Right Ctrl)
    //  Alt           |  7          | 1d
    //

    bool ctrl_alt_keys_pressed=false;
    uint8_t keys[16];
    int rc,i,j;
    
    rc = ioctl (udev_handle, EVIOCGKEY(sizeof keys), &keys);
    if (rc < 0) {
        return false;
    }

    if (verbose) {
        // Dump the key value masks returned by IOCTL EVIOCGKEY
        printf ("key device id: %d\n", udev_handle);
        for (i=0; i < 16; i++) {
            printf ("  key[%02d]=%04dd\n", i, keys[i]);
        }
        printf ("\n");
    }

    // Detect if Left or Right Ctrl + Alt keys are pressed
    if ( (keys[3] == 32 || keys[12] == 2) && (keys[7] == 1) ) {

        ctrl_alt_keys_pressed=true;
        if (verbose) {
            printf ("Ctrl + Alt reported to be pressed, making sure no more keys are pressed\n");
        }

        // make sure no other keys are pressed
        for (i=0; i < 16; i++) {
            if ((i != 3 && i != 12 && i != 7) && keys[i]) {
                // There is an extra key being pressed, assume the hotkey is not up
                ctrl_alt_keys_pressed=false;
                break;
            }
        }
    }

    return ctrl_alt_keys_pressed;
}

HID_HANDLE hid_init(int flags)
{
    int n=0;
    char buf[BUFF_SIZE];

    // Allocate a structure to hold a list of HID devices
    HID_HANDLE hid=(HID_HANDLE) calloc (sizeof (HID_STRUCT), 1);
    if (!hid) {
        return NULL;
    }

    // Give a gratious time for the input event streams to flush type-ahead events
    usleep (GRACE_START_TIME * 1000);

    // Open all possible input devices (keyboard / mouse),
    // save their fd like handles
    // Emptying any possible type-ahead events.

    hid->fdkbd0 = open(chkbd0, O_RDWR | O_NOCTTY | O_NDELAY);
    if (hid->fdkbd0 != -1) {
        fcntl(hid->fdkbd0, F_SETFL, O_NONBLOCK);
        n=read(hid->fdkbd0, (void*)buf, sizeof(buf));
    }

    hid->fdkbd1 = open(chkbd1, O_RDWR | O_NOCTTY | O_NDELAY);
    if (hid->fdkbd1 != -1) {
        fcntl(hid->fdkbd1, F_SETFL, O_NONBLOCK);
        n=read(hid->fdkbd1, (void*)buf, sizeof(buf));
    }

    hid->fdkbd2 = open(chkbd2, O_RDWR | O_NOCTTY | O_NDELAY);
    if (hid->fdkbd2 != -1) {
        fcntl(hid->fdkbd2, F_SETFL, O_NONBLOCK);
        n=read(hid->fdkbd2, (void*)buf, sizeof(buf));
    }
    
    hid->fdmouse0 = open(chmouse0, O_RDWR | O_NOCTTY | O_NDELAY);
    if (hid->fdmouse0 != -1) {
        fcntl(hid->fdmouse0, F_SETFL, O_NONBLOCK);
        n=read(hid->fdmouse0, (void*)buf, sizeof(buf));
    }

    hid->fdmouse1 = open(chmouse1, O_RDWR | O_NOCTTY | O_NDELAY);
    if (hid->fdmouse1 != -1) {
        fcntl(hid->fdmouse1, F_SETFL, O_NONBLOCK);
        n=read(hid->fdmouse1, (void*)buf, sizeof(buf));
    }

    hid->fdmice = open(chmice, O_RDWR | O_NOCTTY | O_NDELAY);
    if (hid->fdmice != -1) {
        fcntl(hid->fdmice, F_SETFL, O_NONBLOCK);
        n=read(hid->fdmice, (void*)buf, sizeof(buf));
    }

    return hid;
}

bool hid_is_user_idle (HID_HANDLE hid, int timeout)
{
    int rc=0;
    fd_set hid_devices;
    struct timeval tv;

    if (!hid) {
        return false;
    }

    // setting timeout member values to zero means return immediately
    // the passed timeout parameter is expressed in seconds.
    tv.tv_sec = timeout;
    tv.tv_usec = 0;

    FD_ZERO(&hid_devices);
    FD_SET(hid->fdkbd0, &hid_devices);
    FD_SET(hid->fdkbd1, &hid_devices);
    FD_SET(hid->fdkbd2, &hid_devices);
    FD_SET(hid->fdmouse0, &hid_devices);
    FD_SET(hid->fdmouse1, &hid_devices);
    FD_SET(hid->fdmice, &hid_devices);

    // return ASAP with indication on wether there is a HID input event or not
    rc = select (6, &hid_devices, NULL, NULL, &tv);
    return ((rc ? true : false));
}

void hid_terminate(HID_HANDLE hid)
{
    // Free HID devices and deallocate wrapped structure
    if (hid != NULL) {
        if (hid->fdkbd0 != -1) close (hid->fdkbd0);
        if (hid->fdkbd1 != -1) close (hid->fdkbd1);
        if (hid->fdkbd2 != -1) close (hid->fdkbd2);
        if (hid->fdmouse0 != -1) close(hid->fdmouse0);
        if (hid->fdmouse1 != -1) close (hid->fdmouse1);
        if (hid->fdmice != -1) close (hid->fdmice);
        
        free (hid);
    }

    return;
}
