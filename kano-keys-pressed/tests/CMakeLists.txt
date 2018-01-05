#
# CMakeLists.txt
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Build file for the tests for kano-keys-pressed
#


cmake_minimum_required (VERSION 2.8.11)

set (CMAKE_CXX_STANDARD 11)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

# Build the Google Test library
add_subdirectory (vendor)

add_executable(
	tests
	src/tests.cpp
	src/test_hotkeys.cpp
)
add_test(NAME check COMMAND tests)

target_include_directories (
    tests
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/stubs
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/include
    ${CMAKE_CURRENT_SOURCE_DIR}/../src
)

# Link against Google Test library
target_link_libraries(tests gmock_main)
