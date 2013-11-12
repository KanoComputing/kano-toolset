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

import sys
import Xlib
import Xlib.display

class FocusClass:
    def __init__(self, display):
        '''
        When you subclass your app, save your application name (arbitrary) and class name tuple
        which identifies your app to the X server - as returned by obxprop / xprop WM_CLASS(STRING)
        '''
        self.appname = None
        self.wclass = (None, None)
        self.display = display

    def get_appname(self):
        return self.appname

    def get_wclass(self):
        return self.wclass

    def kano_focus(self):
        '''
        Implement this function if your app needs to do
        particular things if the user presses the "Kano Focus" key
        and your app has the current input focus.
        Return a meaningul non-zero (int) if you performed some action.
        '''
        print 'nothing to be done'
        return 0

    def _findwindow_(self, windowname):
        screen = self.display.screen() 
        root = screen.root  
        tree = root.query_tree() 
        wins = tree.children 
        for win in wins: 
            wname = win.get_wm_name()
            if wname != None: print wname, win
            if wname == windowname:
                return win
        return None

    def sendkey(self, key):
        Xlib.ext.xtest.fake_input(self.display, Xlib.X.KeyPress, key)

    def setfocus(self, windowname):
        '''
        Sets focus to the window with title name <windowname>.
        Returns True on success, False on failure.
        '''
        w = self._findwindow_ (windowname)
        if w:
            print 'forcing focus to', w
            w.raise_window()
            w.set_input_focus(Xlib.X.RevertToParent, Xlib.X.CurrentTime)
            self.display.sync()
            return True

        return False

class FocusMakeMinecraft (FocusClass):
    '''
    Minecraft's Midori workspace
    '''
    def __init__(self, display):
        FocusClass.__init__(self, display)
        self.appname = 'Make Minecraft'
        self.wclass = ('make-minecraft', 'Make-minecraft')
    def kano_focus(self):
        return self.setfocus('Minecraft - Pi edition')

class FocusMinecraft (FocusClass):
    '''
    '''
    def __init__(self, display):
        FocusClass.__init__(self, display)
        self.appname = 'Minecraft'
        self.wclass = ('make-minecraft', 'Make-minecraft')
    def kano_focus(self):
        return self.setfocus('Make Minecraft')

class FocusMakePong (FocusClass):
    '''
    Pong - The Midori workspace
    '''
    def __init__(self, display):
        FocusClass.__init__(self, display)
        self.appname = 'Make Pong'
        self.wclass = ('make-pong', 'Make Pong')
    def kano_focus(self):
        return self.sendkey('<f8>')

class FocusPong (FocusClass):
    '''
    Pong - The game window
    '''
    def __init__(self, display):
        FocusClass.__init__(self, display)
        self.appname = 'Pong'
        self.wclass = ('pong', 'Pong')
    def kano_focus(self):
        return self.setfocus('Make Pong')


if __name__ == '__main__':

    lockfile = '/tmp/make-focus.lock'
    focused = False
    display = Xlib.display.Display()

    # reentrancy protection

    # List of Kano applications sensitive to the Focus hotkey press
    kano_wins = [ FocusMakeMinecraft(display), FocusMinecraft(display),
                  FocusMakePong(display), FocusPong(display) ]

    # Find the window with current input focus
    f = display.get_input_focus()
    fname  = f.focus.get_wm_name()
    fclass = f.focus.get_wm_class()
    print 'Current focused window:', f, fname, fclass

    for w in kano_wins:
        if w.get_wclass() == fclass:
            print 'Calling %s set focus...' % w.get_appname()
            focused = w.kano_focus()

    sys.exit(focused)
