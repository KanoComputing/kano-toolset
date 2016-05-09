/**
 *
 * kano_network.cpp
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano Toolset functions and C++
 *
 *     kano.network
 *
 */


#include <Python.h>
#include <unordered_map>

#include <kano/python/python_helpers.h>
#include "kano_bindings.h"


std::unordered_map<std::string, std::string> parse_dict(PyObject *py_dict)
{
    std::unordered_map<std::string, std::string> dict;

    PyObject *py_key;
    PyObject *py_value;
    std::string key;
    std::string value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(py_dict, &pos, &py_key, &py_value)) {
        if (py_key != Py_None && Py_TYPE(py_key) == &PyString_Type) {
            key = PyString_AsString(py_key);
        } else {
            key = "";
        }

        if (py_value != Py_None && Py_TYPE(py_value) == &PyString_Type) {
            value = PyString_AsString(py_value);
        } else {
            value = "";
        }

        dict[key] = value;
    }

    return dict;
}


kano::network::network():
    Binding(KANO_NETWORK)
{
}


std::unordered_map<std::string, std::string> kano::network::get_network_info() const
{
    std::unordered_map<std::string, std::string> info;

    PyObject *py_info = this->run_func("network_info");

    if (py_info == NULL || !PyDict_Check(py_info) || PyDict_Size(py_info) == 0)
        return info;

    PyObject *values = PyDict_Values(py_info);
    PyObject *iface_details = PyList_GetItem(values, 0);

    info = parse_dict(iface_details);

    Py_CLEAR(py_info);

    return info;
}
