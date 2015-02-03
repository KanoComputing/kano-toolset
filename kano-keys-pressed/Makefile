#
# kano-keys-pressed
#
#  A tool to detect key modifers being pressed (Shift, Ctrl, Alt, ...)
#

all: kano-keys-pressed

kano-keys-pressed: kano-keys-pressed.o hid.o
	g++ -g kano-keys-pressed.o hid.o -o kano-keys-pressed

hid.o: hid.cpp
	g++ -c -g hid.cpp

kano-keys-pressed.o: kano-keys-pressed.cpp
	g++ -c kano-keys-pressed.cpp
