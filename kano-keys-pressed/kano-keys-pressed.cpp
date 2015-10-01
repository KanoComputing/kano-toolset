//
//  kano-keys-pressed.cpp
//
//  Copyright (C) 2015 Kano Computing Ltd.
//  License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
//  A tool to detect key modifers being pressed (Shift, Ctrl, Alt, ...)
//

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <iostream>
#include <unistd.h>

#include "hid.h"

using namespace std;

int main(int argc, char *argv[])
{
    HID_HANDLE hhid;
    bool is_hotkey=false;
    bool verbose=false;
    int c=0, retry=5, delay=1000;

    while ((c = getopt(argc, argv, "?hvr:d:")) != EOF)
        {
            switch (c)
                {
                case '?':
                case 'h':
                    cout << "kano-keys-pressed [ -? | -h | -v | -r retry_times (default=" << retry << ") ";
                    cout << "| -d delay (default=" << delay << "ms) ]" << endl;
                    return 0;
                case 'v':
                    verbose=true;
                    break;
                case 'r':
                    retry=atoi(optarg);
                    break;
                case 'd':
                    delay=atoi(optarg);
                    break;
                }
        }

    // Ask if any key modifiers are being pressed
    do {
        // Open, read and close access to the keyboard
        // to allow the kernel to refresh any /dev/input mappings
        hhid=hid_init(0);
        if (hhid) {
            is_hotkey = is_hotkey_pressed(hhid, verbose);
            hid_terminate(hhid);
        }
        if (verbose) {
            cout << "is hotkey pressed? " << (is_hotkey ? "Yes" : "No") << endl;
        }

        if (is_hotkey) {
            retry=0;
        }
        else {
            if (--retry > 0) {
                usleep(delay * 1000);
            }
        }

    } while (retry > 0);

    // TODO: Map each key modifier to a value multiplier,
    // so we can explain exactly which keys are being pressed
    exit((is_hotkey == true) ? 10 : 0);
}
