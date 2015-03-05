## uinput

This tool is a modification from Robert Thomson PyInputEvent project at: https://github.com/rmt/pyinputevent
It is used as an internal tool to add the capability to simulate keyboard events into the Linux system.

To send a keyboard event you will first need to know the scancode, then you can do:

```
$ sudo python uinptu <scandcode>
```

You can find most scancodes in the module `scancodes.py`.

This is an experimental tool which is not reliable enough, hence it is not currently used or packaged into KanoOS.
