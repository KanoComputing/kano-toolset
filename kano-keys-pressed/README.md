## kano-keys-pressed


This tool is used in KanoOS to detect if a selection of hotkeys are being
pressed during boot in order to switch to a *safe mode* display settings.


### Usage

Usage is pretty straightforward, run `kano-keys-pressed` while holding some keys
keys down and it will return the following values for the keys (and zero
otherwise)

Registered hotkeys:

    | Key                      | Return Code |
    | :----------------------: | :---------: |
    | Ctrl + Alt               | 1           |
    | Ctrl + Alt + 1           | 2           |
    | Ctrl + Alt + 1           | 3           |

Two options are available to allow for some delay time in detecting the keys.

`-r` sets a number of times the key combination is checked on the keyboard.
`-d` sets a delay time in milliseconds to wait between each retry.

Call `kano-keys-pressed -h` to get a comprehensive help page. Also the `-v` flag
will emit information messages to explain what is going on.


### Building

```
cmake .
make
./kano-keys-pressed
```


### Tests

```
cd tests
cmake .
make
./tests
```
