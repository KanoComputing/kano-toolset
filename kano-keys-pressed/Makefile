#
# kano-keys-pressed
#
#  A tool to detect key modifers being pressed (Shift, Ctrl, Alt, ...)
#

all: kano-keys-pressed

kano-keys-pressed: kano-keys-pressed.o hid.o
	gcc kano-keys-pressed.o hid.o -o kano-keys-pressed

hid.o: hid.cpp
	gcc -c hid.cpp

kano-keys-pressed.o: kano-keys-pressed.cpp
	gcc -c kano-keys-pressed.cpp
