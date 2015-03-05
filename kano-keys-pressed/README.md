## kano-keys-pressed

This tool is used in KanoOS to detect the keys Ctrl-Alt are being pressed during boot,
and switch to a *safe mode* display settings.

Usage is pretty straightforward, run `kano-keys-pressed` while holding the Ctrl-Alt keys down,
and it will return with rc=10, or zero otherwise.

Two options are available to allow for some delay time in detecting the keys.

`-r` sets a number of times the key combination is checked on the keyboard.
`-d` sets a delay time in milliseconds to wait between each retry.

Call `kano-keys-pressed -h` to get a comprehensive help page. Also the `-v` flag will emit
information messages to explain what is going on.
