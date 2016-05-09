/**
 * python_helpers.h
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Provide functions to assist calling Python modules
 */


#ifndef __PYTHON_HELPERS_H__
#define __PYTHON_HELPERS_H__

#include <Python.h>
#include <string>

PyObject *new_pyobject(PyObject *o);
PyObject *new_pyobject(int o);
PyObject *new_pyobject(long o);
PyObject *new_pyobject(double o);
PyObject *new_pyobject(bool o);
PyObject *new_pyobject(std::string o);
PyObject *new_pyobject(char *o);
void fill_tuple(PyObject *tuple, int pos);


template<typename Type, typename... Args>
void fill_tuple(PyObject *tuple, int pos, Type arg1, Args... args)
{
    PyObject *py_arg = new_pyobject(arg1);
    PyTuple_SetItem(tuple, pos, py_arg);

    if (sizeof...(args) > 0)
        fill_tuple(tuple, pos + 1, args...);
}


/**
 * Creates a new tuple packed with PyObject* converted args.
 *
 * Note: Returns new reference to tuple
 */
template<typename... Args>
PyObject *new_tuple(Args... args)
{
    PyObject *tuple = PyTuple_New(sizeof...(args));
    fill_tuple(tuple, 0, args...);

    return tuple;
}


class Binding {
    public:
        Binding(const std::string module_str);
        ~Binding();
    protected:
        PyObject *run_func(const std::string function_name, PyObject *args = NULL) const;

        const std::string module_name;
        PyObject *module;
};


#endif
