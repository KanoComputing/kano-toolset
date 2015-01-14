#
# Placeholder makefile so "debuild" can be gently persuaded to work
#

.PHONY: kano-keys-pressed

all: kano-keys-pressed

kano-keys-pressed:
	cd kano-keys-pressed && make
