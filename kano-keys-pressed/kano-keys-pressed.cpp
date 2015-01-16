//
// kano-keys-pressed.cpp
//
//  A tool to detect key modifers being pressed (Shift, Ctrl, Alt, ...)
//

#include <stdio.h>
#include <stdlib.h>

#include "hid.h"

int main(int argc, char *argv[])
{
    HID_HANDLE hhid;
    bool is_hotkey=false;

    // initialize access to input devices
    hhid=hid_init(0);

    // Ask if any key modifiers are being pressed
    is_hotkey = is_hotkey_pressed(hhid);

    if (argc > 1 && argv[1] == "-v") {
        printf ("is key held? %s\n", is_hotkey ? "Yes" : "No");
    }

    // Free access to HID devices
    hid_terminate(hhid);

    // TODO: Map each key modifier to a value multiplier,
    // so we can explain exactly which keys are being pressed
    exit((is_hotkey == true) ? 10 : 0);
}
