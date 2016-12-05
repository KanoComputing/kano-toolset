/**
 * json_helpers.h
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Simplifications to the Parson library
 * TODO: Fix install path
 *
 */


#ifndef __JSON_HELPERS_H__
#define __JSON_HELPERS_H__


#include <iostream>
#include <string>
#include <vector>
#include <parson/parson.h>


// ----------------------------------------------------------------


template<typename T>
inline T get_json_val(__attribute__((unused)) const JSON_Object *root, __attribute__((unused)) const std::string key)
{
    return T();
}

template <>
inline double get_json_val<double>(const JSON_Object *root, const std::string key)
{
    return json_object_get_number(root, key.c_str());
}


template <>
inline int get_json_val<int>(const JSON_Object *root, const std::string key)
{
    return static_cast<int>(
        get_json_val<double>(root, key)
    );
}


template <>
inline std::string get_json_val<std::string>(const JSON_Object *root, const std::string key)
{
    const char *val = json_object_get_string(root, key.c_str());

    if (!val)
        return "";

    return std::string(val);
}


template <>
inline bool get_json_val<bool>(const JSON_Object *root, const std::string key)
{
    return json_object_get_boolean(root, key.c_str()) == 1;
}


// ----------------------------------------------------------------


template<typename T>
inline T get_json_val(__attribute__((unused)) const JSON_Value *root)
{
    return T();
}


template<>
inline double get_json_val(const JSON_Value *node)
{
    if (json_value_get_type(node) != JSONNumber) {
        std::cout << "JSON value isn't of string type\n";
        return double();
    }

    return json_value_get_number(node);
}


template <>
inline int get_json_val<int>(const JSON_Value *node)
{
    return static_cast<int>(
        get_json_val<double>(node)
    );
}


template<>
inline std::string get_json_val(const JSON_Value *node)
{
    if (json_value_get_type(node) != JSONString) {
        std::cout << "JSON value isn't of string type\n";
        return std::string();
    }

    return json_value_get_string(node);
}


template <>
inline bool get_json_val<bool>(const JSON_Value *node)
{
    return json_value_get_boolean(node) == 1;
}


// ----------------------------------------------------------------


template<typename T>
inline std::vector<T> get_json_array(const JSON_Object *root, const std::string key)
{
    std::vector<T> vals;

    if (!root) {
        std::cout << "Root node is null\n";
        return vals;
    }

    JSON_Value *node = json_object_get_value(root, key.c_str());

    if (!node) {
        std::cout << "Invalid key (" << key << ") for JSON\n";
        return vals;
    }

    if (json_value_get_type(node) != JSONArray) {
        std::cout << "Value for JSON key '" << key << "' is not an array.\n";
        return vals;
    }

    JSON_Array *arr = json_value_get_array(node);
    size_t len = json_array_get_count(arr);

    for (size_t i = 0; i < len; i++) {
        JSON_Value * val = json_array_get_value(arr, i);
        vals.push_back(get_json_val<T>(val));
    }

    return vals;
}


/**
 * A safe version of `json_object_get_string`
 */
inline std::string get_json_string(const JSON_Object *root, const std::string key)
{
    return get_json_val<std::string>(root, key);
}


#endif
