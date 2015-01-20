//
// kano-keys-pressed.cpp
//
//  A tool to detect key modifers being pressed (Shift, Ctrl, Alt, ...)
//

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "hid.h"

int main(int argc, char *argv[])
{
    HID_HANDLE hhid;
    bool is_hotkey=false;
    bool verbose=false;

    if (argc > 1 && !(strcmp(argv[1], "-v"))) {
        verbose=true;
    }

    // initialize access to input devices
    hhid=hid_init(0);

    // Ask if any key modifiers are being pressed
    is_hotkey = is_hotkey_pressed(hhid, verbose);

    // Free access to HID devices
    hid_terminate(hhid);

    if (verbose) {
        printf ("is hotkey pressed? %s\n", is_hotkey ? "Yes" : "No");
    }

    // TODO: Map each key modifier to a value multiplier,
    // so we can explain exactly which keys are being pressed
    exit((is_hotkey == true) ? 10 : 0);
}
