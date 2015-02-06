#kano-get-start-time/* kano-get-start-time.c
# 
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# 
# Build file for kano-splash and related utilities.
#

all: kano-splash kano-get-start-time

kano-splash: kano-splash.cpp
	g++ -fpermissive -g $<  -lX11 -lImlib2  -o $@

kano-get-start-time: kano-get-start-time.c get-start-time.c
	g++ -g $^  -o $@
