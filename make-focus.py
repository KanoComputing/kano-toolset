#!/usr/bin/python
#
#  This module gets called when Kano "Focus" key is pressed.
#  It finds the currently active window, decides if/where focus needs to go and switches focus.
#
#  This script is fired by openbox, it is registered in the lxde xml file, 
#  normally ~/config/openbox/lxde-rc.xml
#
#  This module requires the debian package: python-xlib
#  Code excerpts collected from: http://thp.io/2007/09/x11-idle-time-and-focused-window-in.html
#  For sending keys: http://autokey.googlecode.com/svn-history/r8/trunk/autokey.py
#  API documentation: http://python-xlib.sourceforge.net/doc/html/python-xlib_16.html
#
#  Returns 0 if no focus action has taken place, non-zero otherwise.
#

import os, sys, atexit
import Xlib
import Xlib.display

def get_active_window():
    '''
    Returns the currently active window name, as returned
    by xprop's _NET_WM_NAME attribute - the window title.
    '''
    wname = None
    cmdline = 'xprop -id $(xdotool getactivewindow)|grep _NET_WM_NAME'
    out = os.popen (cmdline).read()
    if len(out):
        try:
            wname = out.split('=')[1]
            wname = wname.strip(' ').strip('\n').strip('"').strip(' ')
        except:
            print 'could not find active window'
            pass

    print 'Currently active window name=', wname
    return wname

def sendkey(key_name):
    '''
    Sends a keyboard event to the X server.
    Returns True if success, False otherwise
    '''
    cmdline = 'xdotool key %s' % (key_name.upper())
    rc = os.system(cmdline)
    if rc == 0:
        print 'key event %s sent' % key_name
        return True
    else:
        return False

def setfocus(windowname):
    '''
    Sets focus to the window with title name <windowname>.
    Returns True on success, False on failure. Waits for focus to be acquired.
    '''
    focused = False
    cmdline = 'xdotool windowfocus --sync $(xdotool search --name "%s" | head -n 1) > /dev/null 2>&1' % windowname
    rc = os.system (cmdline)
    if rc == 0:
        print 'focus changed to window "%s"' % windowname
        focused = True
    else:
        print 'error sending focus - rc=%d' % os.WEXITSTATUS(rc)

    return focused

class FocusClass:
    def __init__(self, display):
        '''
        When you subclass your app, save your application name, as reported by xprop _NET_WM_NAME(UTF8_STRING)
        '''
        self.appname = None
        self.display = display

    def get_appname(self):
        return self.appname

    def kano_focus(self):
        '''
        Implement this function if your app needs to do
        particular things if the user presses the "Kano Focus" key
        and your app has the current input focus.
        Return a meaningul non-zero (int) if you performed some action.
        '''
        print 'nothing to be done'
        return 0

class FocusMakeMinecraft (FocusClass):
    '''
    Minecraft's Midori workspace
    '''
    def __init__(self, display):
        FocusClass.__init__(self, display)
        self.appname = 'Make Minecraft'
    def kano_focus(self):
        '''
        Push the Make button.
        '''
        os.system ('/usr/sbin/make-minecraft.sh $HOME/Minecraft-content/minecraft.py &')
        return setfocus('Minecraft - Pi edition')

class FocusMinecraft (FocusClass):
    '''
    Minecraft - The game window
    '''
    def __init__(self, display):
        FocusClass.__init__(self, display)
        self.appname = 'Minecraft'
    def kano_focus(self):
        return setfocus('Make Minecraft')

class FocusMakePong (FocusClass):
    '''
    Pong - The Midori workspace
    '''
    def __init__(self, display):
        FocusClass.__init__(self, display)
        self.appname = 'Make Pong'
    def kano_focus(self):
        return sendkey('f8')

class FocusPong (FocusClass):
    '''
    Pong - The game window
    '''
    def __init__(self, display):
        FocusClass.__init__(self, display)
        self.appname = 'Pong'
    def kano_focus(self):
        return setfocus('Make Pong')

def lock_file(fname):
    ''' TODO: Use a more robust file locking method,
    for example: http://stackoverflow.com/questions/5339200/how-to-create-a-single-instance-application-in-c/5339606#5339606
    '''
    if os.access (fname, os.R_OK):
        return False
    else:
        f = open (fname, 'w')
        f.write('make-focus-locked')
        f.close()
        return True

def unlock_file(fname):
    os.unlink(fname)

if __name__ == '__main__':

    lock_filename = '/tmp/make-focus.lock'
    focused = False
    display = Xlib.display.Display()

    # reentrancy protection
    atexit.register (unlock_file, fname=lock_filename)
    if lock_file(lock_filename) == False:
        sys.exit(-1)

    # List of Kano applications sensitive to the Focus hotkey press
    kano_wins = [ FocusMakeMinecraft(display), FocusMinecraft(display),
                  FocusMakePong(display), FocusPong(display) ]

    active_window_name = get_active_window()
    if active_window_name and len(active_window_name) > 0:
        print 'Active window _NET_WM_NAME(UTF8_STRING) = "%s"' % active_window_name
        for w in kano_wins:
            if active_window_name.find (w.appname) != -1:
                print 'Calling "%s" class set focus...' % w.get_appname()
                focused = w.kano_focus()
                break

    sys.exit(focused)
