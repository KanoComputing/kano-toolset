#
# Placeholder makefile so "debuild" can be gently persuaded to work
#

REPO:= kano-toolset


.PHONY: clean docs kano-keys-pressed kano-launcher kano-logging kano kano-networking kano-python parson check test

all: kano-keys-pressed kano-launcher kano kano-networking kano-python parson

clean:
	cd docs && make clean

docs:
	cd docs && make all

kano-keys-pressed:
	cd kano-keys-pressed && make

kano-launcher: kano-c-logging
	cd kano-launcher && make

kano-c-logging:
	cd libs/kano-c-logging && make
	cd libs/kano-c-logging && make debug


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

#
# Add test targets
#
include pythontest.mk
check: pythontest
test: check
