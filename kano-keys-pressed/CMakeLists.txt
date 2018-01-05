#
# CMakeLists.txt
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Build file for kano-keys-pressed
#


cmake_minimum_required (VERSION 2.8.11)

set (CMAKE_CXX_STANDARD 11)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

add_executable(
	kano-keys-pressed
    src/kano-keys-pressed.cpp
    src/hid.cpp
    src/hotkeys.cpp
)
target_include_directories (
    kano-keys-pressed
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/include
)

# Uncomment for tests
# include(CTest)
# enable_testing()

if(BUILD_TESTING)
    add_subdirectory (tests)
endif()
