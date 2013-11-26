#!/bin/bash
#
#  Script to shutdown the system after a confirmation message
#  on the graphic frontend. The user needs sudo NOPASSWD: privileges for /sbin/poweroff.
#

set -e

zenity --question --title "Warning: Kanux Shutdown"  --text "Are you sure you want to shutdown?"
if [ $? == 0 ]; then
   sudo /sbin/poweroff
fi
