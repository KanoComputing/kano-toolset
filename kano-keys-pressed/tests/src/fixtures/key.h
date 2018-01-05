/**
 * keys.h
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
 *
 * Basic structure to hold a key
 *
 */


#ifndef __FIXTURES_KEY_H__
#define __FIXTURES_KEY_H__


// Test framework
#include "gtest/gtest.h"

// Lib dependencies
#include <inttypes.h>


class Key
{
    public:
        Key(uint8_t key_bit = 0, uint8_t byte = 0, uint8_t val = 0) :
            key_bit(key_bit),
            byte(byte),
            val(val)
        {
        }
        uint8_t key_bit;
        uint8_t byte;
        uint8_t val;

        bool operator<(const Key &other) const
        {
            return this->key_bit < other.key_bit;
        }
        bool operator<=(const Key &other) const
        {
            return this->key_bit <= other.key_bit;
        }
        bool operator>(const Key &other) const
        {
            return this->key_bit > other.key_bit;
        }
        bool operator>=(const Key &other) const
        {
            return this->key_bit >= other.key_bit;
        }
        bool operator==(const Key &other) const
        {
            return this->key_bit == other.key_bit;
        }
        bool operator!=(const Key &other) const
        {
            return this->key_bit != other.key_bit;
        }
        std::string debug_string(bool verbose = false) const
        {
            std::string debug = Key::key_bit_to_str(this->key_bit);

            if (verbose) {
                debug += " (bit: " + std::to_string(static_cast<int>(this->key_bit))
                    + ") [byte: " + std::to_string(static_cast<int>(this->byte))
                    + ", val: " + std::to_string(static_cast<int>(this->val))
                    + "]";
            }

            return debug;
        }

        static std::string key_bit_to_str(uint8_t bit)
        {
            switch (bit) {
            case KEY_1:
                return "KEY_1";
            case KEY_2:
                return "KEY_2";
            case KEY_3:
                return "KEY_3";
            case KEY_4:
                return "KEY_4";
            case KEY_5:
                return "KEY_5";
            case KEY_6:
                return "KEY_6";
            case KEY_7:
                return "KEY_7";
            case KEY_8:
                return "KEY_8";
            case KEY_9:
                return "KEY_9";
            case KEY_0:
                return "KEY_0";
            case KEY_LEFTCTRL:
                return "KEY_LEFTCTRL";
            case KEY_LEFTSHIFT:
                return "KEY_LEFTSHIFT";
            case KEY_RIGHTSHIFT:
                return "KEY_RIGHTSHIFT";
            case KEY_LEFTALT:
                return "KEY_LEFTALT";
            case KEY_RIGHTCTRL:
                return "KEY_RIGHTCTRL";
            case KEY_RIGHTALT:
                return "KEY_RIGHTALT";
            case KEY_LEFTMETA:
                return "KEY_LEFTMETA";
            default:
                return "";
            }
        }
};


/**
 * Pretty print Key rather than binary dump
 */
std::ostream& operator<<(::std::ostream& os, const Key& key) {
    return os << key.debug_string();
}


#endif  // __FIXTURES_KEY_H__
