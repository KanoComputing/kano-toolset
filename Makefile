#
# Placeholder makefile so "debuild" can be gently persuaded to work
#

REPORT_DIR = reports
COVERAGE_REPORT_DIR = $(REPORT_DIR)/coverage
TESTS_REPORT_DIR = $(REPORT_DIR)/tests

# Elaborate mechanism just to get the correct syntax for the pytest markers param
_FIRST_TAG := $(firstword $(OMITTED_TAGS))
PYTEST_TAGS_EXPR := $(foreach tag, $(OMITTED_TAGS), $(if $(filter $(tag), $(_FIRST_TAG)),not $(tag),and not $(tag)))

ifeq ($(PYTEST_TAGS_EXPR), )
	PYTEST_TAGS_FLAG :=
else
	PYTEST_TAGS_FLAG := -m "$(strip $(PYTEST_TAGS_EXPR))"
endif
BEHAVE_TAGS_FLAG := $(join $(addprefix --tags=-,$(OMITTED_TAGS)), $(space))


.PHONY: clean docs kano-keys-pressed kano-launcher kano-logging kano kano-networking kano-python parson check test

all: kano-keys-pressed kano-launcher kano kano-networking kano-python parson

clean:
	cd docs && make clean

docs:
	cd docs && make all

kano-keys-pressed:
	cd kano-keys-pressed && cmake . && make

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
# Run the tests
#
# Requirements:
#     - pytest
#     - behave
#     - pytest-cov
#
check:
	# Refresh the reports directory
	rm -rf $(REPORT_DIR)
	mkdir -p $(REPORT_DIR)
	mkdir -p $(COVERAGE_REPORT_DIR)
	mkdir -p $(TESTS_REPORT_DIR)
	# Run the tests
	-coverage run --module pytest $(PYTEST_TAGS_FLAG) --junitxml=$(TESTS_REPORT_DIR)/pytest_results.xml
	-coverage run --append --module behave $(BEHAVE_TAGS_FLAG) --junit --junit-directory=$(TESTS_REPORT_DIR)
	# Generate reports
	coverage xml
	coverage html
	coverage-badge -o $(COVERAGE_REPORT_DIR)/kano-toolset-coverage.svg

test: check
