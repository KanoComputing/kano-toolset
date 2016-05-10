/**
 *
 * utils_audio.cpp
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano Toolset functions and C++
 *
 *     kano.utils.audio
 *
 */


#include <Python.h>
#include <string>

#include <kano/python/python_helpers.h>
#include "kano/kano/kano_bindings.h"


kano::utils::audio::audio():
    Binding(KANO_UTILS_AUDIO)
{
}


bool kano::utils::audio::play_sound(const std::string audio_file, const bool background) const
{
    PyObject *py_success = this->run_func(
        "play_sound",
        new_tuple(audio_file, background)
    );

    if (py_success == NULL)
        return false;

    bool success = PyBool_Check(py_success)
            && py_success == Py_True;

    Py_CLEAR(py_success);

    return success;
}


long kano::utils::audio::percent_to_millibel(const int percent, const bool raspberry_mod) const
{
    PyObject *py_milli = this->run_func(
        "percent_to_millibel",
        new_tuple(percent, raspberry_mod)
    );

    if (py_milli == NULL)
        return 0;

    if (!PyInt_Check(py_milli)) {
        Py_CLEAR(py_milli);
        return 0;
    }

    long milli = PyInt_AsLong(py_milli);
    Py_CLEAR(py_milli);

    return milli;
}


long kano::utils::audio::get_volume() const
{
    PyObject *py_vol = this->run_func("get_volume");

    if (py_vol == NULL)
        return 0;

    if (!PyInt_Check(py_vol)) {
        Py_CLEAR(py_vol);
        return 0;
    }

    long vol = PyInt_AsLong(py_vol);
    Py_CLEAR(py_vol);

    return vol;
}


void kano::utils::audio::set_volume(float percent) const
{
    this->run_func(
        "set_volume",
        new_tuple(percent)
    );
}
