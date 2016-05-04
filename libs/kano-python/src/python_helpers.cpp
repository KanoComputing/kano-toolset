/**
 * python_helpers.cpp
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Provide functions to assist calling Python modules
 */


#include <Python.h>
#include <string>
#include <iostream>

#include "python_helpers.h"


/**
 * For simplicity add this function which does nothing
 */
PyObject *new_pyobject(PyObject *o)
{
    return o;
}


PyObject *new_pyobject(long o)
{
    return PyInt_FromLong(o);
}


PyObject *new_pyobject(double o)
{
    return PyFloat_FromDouble(o);
}


PyObject *new_pyobject(std::string o)
{
    return PyString_FromString(o.c_str());
}


PyObject *new_pyobject(char *o)
{
    return PyString_FromString(o);
}


Binding::Binding(const std::string module_str):
    module_name(module_str)
{
    if (Py_IsInitialized() == 0)
        Py_InitializeEx(0);

    PyGILState_STATE state = PyGILState_Ensure();

    this->module = PyImport_ImportModule(this->module_name.c_str());

    if (module == NULL) {
        std::cout << "Error: Module couldn't be imported\n";
    }

    PyGILState_Release(state);
}


Binding::~Binding()
{
    Py_CLEAR(this->module);
}


/**
 * Run a function in the object's module
 *
 * Note: Steals the reference to `args` so that (like `PyTuple_SetItem`) it can
 *       be called as `run_func("function_name", new_tuple(arg1, arg2, ...))`
 */
PyObject *Binding::run_func(const std::string function_name, PyObject *args) const
{
    if (this->module == NULL) {
        std::cout << "Error: Module couldn't be imported\n";
        return NULL;
    }

    PyObject *func = PyObject_GetAttrString(
        this->module, function_name.c_str()
    );

    if (func == NULL) {
        std::cout << "Error: Function couldn't be found\n";
        return NULL;
    }

    if (args == NULL)
        args = PyTuple_New(0);

    PyObject *ret = PyObject_CallObject(func, args);

    if (ret == Py_None) {
        Py_CLEAR(ret);
    }

    Py_CLEAR(func);
    Py_CLEAR(args);

    return ret;
}
