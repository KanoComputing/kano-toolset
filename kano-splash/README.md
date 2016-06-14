### Kano Splash

Kano Splash tool allows to show alert messages on top of all applications very fast!

This directory builds kano-splash and kano-get-start-time

The former is derived from pngview in https://github.com/AndrewFromMelbourne/raspidmx which uses low-level rpi gpu apis.

### Usage

kano-splash can be added as a command line interpreter to launch a splash screen. Eg, change

```
#!/usr/bin/env python 
```

to 

```
#!/usr/bin/kano-splash /usr/share/kano-foo/splash/png /usr/bin/env python 
```

The app mush then call `system("kano-stop-splash")` to stop the splash (or wait for it to time out at 15 seconds).

Parameters can also be passed on the shebang with the ampersand delimiter, for example:

```
#!/usr/bin/kano-splash /usr/share/kano-foo/splash/png&t=60&b=0xffff /usr/bin/env python 
```

Would set the timeout to 60 seconds and show the splash image on a white background.

Alternatively, the app can call:

```
 $ kano-start-splash -b <alpha> -t  <timeout> <splashfile>
```

Which is a symbolic link to `kano-splash`.

It must then save the PID and start time so that `kano-stop-splash` can determine which process to signal.
This is how to do that in bash:

```
SPLASH_PID=$!
SPLASH_START_TIME=$(kano-get-start-time $SPLASH_PID)
export SPLASH_PID SPLASH_START_TIME
```

Enjoy!
