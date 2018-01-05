/*
 *  kano-keys-pressed.cpp
 *
 *  Copyright (C) 2015-2018 Kano Computing Ltd.
 *  License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
 *
 *  A tool to detect key modifers being pressed (Shift, Ctrl, Alt, ...)
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <iostream>
#include <unistd.h>

#include "hid.h"
#include "hotkeys.h"

using namespace std;


int main(int argc, char *argv[])
{
    HID_HANDLE hhid;
    Hotkey pressed_hotkey;
    bool verbose = false;
    int arg = 0, retry = 5, delay = 1000;

    while ((arg = getopt(argc, argv, "?hvr:d:")) != EOF) {
        switch (arg) {
        case '?':
        case 'h':
            cout << "Usage:\n"
                 << "    kano-keys-pressed [options]\n"
                 << "\n"
                 << "Options: \n"
                 << "    -h, -?        This help dialog\n"
                 << "    -v            Verbose mode\n"
                 << "    -d delay      Delay between tries (default = " << delay << "ms)\n"
                 << "    -r retries    Number of times to retry (default = " << retry << ")\n";
            return 0;
        case 'v':
            verbose = true;
            break;
        case 'r':
            retry = atoi(optarg);
            break;
        case 'd':
            delay = atoi(optarg);
            break;
        }
    }

    // Ask if any key modifiers are being pressed
    do {
        // Open, read and close access to the keyboard
        // to allow the kernel to refresh any /dev/input mappings
        hhid = hid_init(0);

        if (hhid) {
            pressed_hotkey = get_pressed_hotkeys(hhid, verbose);
            hid_terminate(hhid);
        }

        if (verbose)
            print_hotkey(pressed_hotkey);

        if (pressed_hotkey != NO_HOTKEY) {
            break;
        }

        if (--retry > 0) {
            usleep(delay * 1000);
        }
    } while (retry > 0);

    // TODO: Map each key modifier to a value multiplier,
    // so we can explain exactly which keys are being pressed
    exit(pressed_hotkey);
}
