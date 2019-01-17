#
# pythontest.mk
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Project-independent python test targets.
#
# Add to main Makefile with:
#
#     include pythontest.mk
#
# Ensure to set the REPO variable in the main Makefile:
#
#     REPO:= my-project
#
# Creates a `pythontest` target which can either be accessed from main Makefile
# or linked to another target, e.g.
#
#     test: pythontest
#

# Run tests, excluding these tagged items, e.g
#     make check OMITTED_TAGS="tag1 tag2"
OMITTED_TAGS =

empty:=
space:= $(empty) $(empty)

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


#
# Run the tests
#
# Requirements:
#     - pytest
#     - behave
#     - pytest-cov
#     - pytest-flake8
#     - pytest-tap
#
pythontest:
	# Refresh the reports directory
	rm -rf $(REPORT_DIR)
	mkdir -p $(REPORT_DIR)
	mkdir -p $(COVERAGE_REPORT_DIR)
	mkdir -p $(TESTS_REPORT_DIR)
	# Run the tests
	-coverage run --module pytest --flake8 --cache-clear $(PYTEST_TAGS_FLAG) --junitxml=$(TESTS_REPORT_DIR)/pytest_results.xml
	-coverage run --append --module behave $(BEHAVE_TAGS_FLAG) --junit --junit-directory=$(TESTS_REPORT_DIR)
	# Generate reports
	coverage xml
	coverage html
	coverage-badge -o $(COVERAGE_REPORT_DIR)/$(REPO)-coverage.svg
