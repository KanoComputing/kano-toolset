#
# Placeholder makefile so "debuild" can be gently persuaded to work
#

.PHONY: kano-keys-pressed kano-splash kano-launcher kano-logging

all: kano-keys-pressed kano-splash kano-launcher

kano-keys-pressed:
	cd kano-keys-pressed && make

kano-splash: kano-logging
	cd kano-splash && make

kano-launcher: kano-logging
	cd kano-launcher && make

kano-logging:
	cd kano-logging && make
