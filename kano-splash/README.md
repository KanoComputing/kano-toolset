### Kano Splash

Kano Splash tool allows to show alert messages on top of all applications very fast!

This directory builds kano-splash and kano-get-start-time.

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

If the second argument points to a directory instead of a png file, it is treated as a short animation video.
The folder must contain a sequence of png files that make up the frames of the animation, with these considerations:

 * The files must all share the same size, colorspace and alpha channel.
 * The filenames must be named in a way that are alphabetically sorted, i.e. frame-001.png, frame-002.png, etc.
 * Use the alpha channel to make the animation transparent on top of all apps.

The app mush then call `system("kano-stop-splash")` to stop the splash (or wait for it to time out at 15 seconds).
In the case of animations, it will be played in an endless loop until the `kano-stop-splash` tool is called.

Alternatively, the app can call

```
 $ kano-start-splash -b <alpha> -t  <timeout> <splashfile>
```

It must then save the PID and start time so that kano-stop-splash can determine which process to signal.
This is how to do that in bash:

```
SPLASH_PID=$!
SPLASH_START_TIME=$(kano-get-start-time $SPLASH_PID)
export SPLASH_PID SPLASH_START_TIME
```

###Testing

Use the `test_splash.sh` script to test it on the RaspberryPI. Change the second argument in the shebang
to either point to a static image or a folder containing a png animation.

Enjoy!
