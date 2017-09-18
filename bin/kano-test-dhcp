#!/usr/bin/python
#
#  Copyright (C) 2015-2017 Kano Computing Ltd.
#  License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#  Simple test for the new DHCP hooks.
#  Searches the systemd journal for entries emitted by the various network scripts
#
#  To run these tests:
#   Enable journalctl adding "Storage=persistent" to /etc/systemd/journalctl.conf
#   Reboot the kit
#   Run this program to expect 0 failures
#
#  Call with "--dump" to query the system logs manually.
#  This test can only succeed on a real RaspberryPI.
#

import os
import sys
import json

failures=0

def testlog(logs, entry, verbose=False):

   global failures
   
   for line in logs:
      if entry in line:
         if verbose:
            print 'PASS: {}'.format(line),
         return True

   failures += 1
   print 'FAIL: {} not found in the logs'.format(entry)


if __name__ == '__main__':

   verbose=True
   dump=False

   if len(sys.argv) > 1 and sys.argv[1] == '--dump':
      dump=True

   patterns=[
      'REBOOT event',
      'launching network up scripts',
      'Started /usr/bin/kano-sentry-startup',
      'Started /usr/bin/kano-network-hook',
      'Started /usr/bin/kano-set-system-date',
      'info Ultimate parental control IS switched on',
      'Started /usr/bin/kano-dashboard-sysupdates',
      'Time has been changed',
      'info rdate SUCCESS'
      ]

   # Collect the journal from the current system bootup sequence alone
   output=os.popen('sudo journalctl --boot=0 | grep "REBOOT" -A 15').readlines()
   if dump:
      for line in output:
         print line,
      sys.exit(0)

   for test in patterns:
      testlog(output, test, verbose=verbose)

   print 'failures={}'.format(failures)
   sys.exit(failures > 0)
