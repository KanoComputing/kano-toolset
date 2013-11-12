#!/usr/bin/python

import sys, os

if __name__ == '__main__':

    if len(sys.argv) == 2:
        cmdline = sys.argv[1]
        rc = os.system(cmdline)
        sys.exit(rc)
    else:
        print 'I need an app command line to execute'
        sys.exit(1)
