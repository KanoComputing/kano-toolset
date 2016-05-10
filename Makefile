#
# Placeholder makefile so "debuild" can be gently persuaded to work
#

.PHONY: kano-keys-pressed kano-splash kano-launcher kano-logging kano kano-networking kano-python parson

all: kano-keys-pressed kano-splash kano-launcher kano kano-networking kano-python parson

kano-keys-pressed:
	cd kano-keys-pressed && make

kano-splash: kano-logging
	cd kano-splash && make

kano-launcher: kano-logging
	cd kano-launcher && make

kano-logging:
	cd kano-logging && make

kano: kano-python
	cd libs/kano && LOCAL_BUILD=1 make
	cd libs/kano && LOCAL_BUILD=1 make debug

kano-networking:
	cd libs/kano-networking && make
	cd libs/kano-networking && make debug

kano-python:
	cd libs/kano-python && make
	cd libs/kano-python && make debug

parson:
	cd libs/parson && make
	cd libs/parson && make debug
