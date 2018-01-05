/**
 * keys_data.h
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
 *
 * Fixtures which provide a parameterised set of keys to pass to a function
 *
 */


#ifndef __FIXTURES_KEYS_DATA_H__
#define __FIXTURES_KEYS_DATA_H__


// Test framework
#include "gtest/gtest.h"

// Lib dependencies
#include <linux/input.h>
#include <string>
#include <tuple>

// Fixtures
#include "fixtures/key.h"


/**
 * A test class for working with Key parameters of varying length as the fixture
 * data.
 */
template <typename T>
class KeysData : public testing::TestWithParam<T>
{
    public:
        virtual void SetUp()
        {
            this->load_keys(this->GetParam());
            memset(this->mask, 0, sizeof this->mask);
        }

        virtual void TearDown()
        {
        }

        void test_add_mask();
        void test_mask_match();

    protected:
        std::vector<Key> keys;
        int key_bit_param;
        uint8_t mask[16];

        virtual void load_keys(T params);
};


/**
 * Template specialization for varying lengths of tuple
 */

template <>
void KeysData<Key>::load_keys(Key key)
{
    this->keys.push_back(key);
}


template <>
void KeysData<std::tuple<Key, Key>>::load_keys(std::tuple<Key, Key> key_tuple)
{
    this->keys.push_back(std::get<0>(key_tuple));
    this->keys.push_back(std::get<1>(key_tuple));
}


template <>
void KeysData<std::tuple<Key, Key, Key>>::load_keys(std::tuple<Key, Key, Key> key_tuple)
{
    this->keys.push_back(std::get<0>(key_tuple));
    this->keys.push_back(std::get<1>(key_tuple));
    this->keys.push_back(std::get<2>(key_tuple));
}


template <>
void KeysData<std::tuple<Key, Key, Key, Key>>::load_keys(std::tuple<Key, Key, Key, Key> key_tuple)
{
    this->keys.push_back(std::get<0>(key_tuple));
    this->keys.push_back(std::get<1>(key_tuple));
    this->keys.push_back(std::get<2>(key_tuple));
    this->keys.push_back(std::get<3>(key_tuple));
}


/**
 * Typedefs for each of these template specializations so that they can be used
 * with INSTANTIATE_TEST_CASE_P's rudimentary #define
 */


typedef class KeysData<Key> KeysDataSingles;
typedef class KeysData<std::tuple<Key, Key>> KeysDataPairs;
typedef class KeysData<std::tuple<Key, Key, Key>> KeysDataTriples;
typedef class KeysData<std::tuple<Key, Key, Key, Key>> KeysDataQuads;


/**
 * Generator for key data
 */


auto key_generator = testing::Values(
    Key(KEY_LEFTALT, 7, 0x1),  // Bit 56
    Key(KEY_RIGHTALT, 12, 0x1 << 4),  // Alt Gr, Bit 100
    Key(KEY_LEFTSHIFT, 5, 0x1 << 2),  // Bit 42
    Key(KEY_RIGHTSHIFT, 6, 0x1 << 6),  // Bit 54
    Key(KEY_LEFTCTRL, 3, 0x1 << 5),  // Bit 29
    Key(KEY_RIGHTCTRL, 12, 0x1 << 1),  // Bit 97
    Key(KEY_LEFTMETA, 15, 0x1 << 5),  // Windows Key, Bit 125
    Key(KEY_1, 0, 0x1 << 2),  // Bit 2
    Key(KEY_2, 0, 0x1 << 3),  // Bit 3
    Key(KEY_3, 0, 0x1 << 4),  // Bit 4
    Key(KEY_4, 0, 0x1 << 5),  // Bit 5
    Key(KEY_5, 0, 0x1 << 6),  // Bit 6
    Key(KEY_6, 0, 0x1 << 7),  // Bit 7
    Key(KEY_7, 1, 0x1),  // Bit 8
    Key(KEY_8, 1, 0x1 << 1),  // Bit 9
    Key(KEY_9, 1, 0x1 << 2),  // Bit 10
    Key(KEY_0, 1, 0x1 << 3)  // Bit 11
);


/**
 * Register data for each KeysData specialization
 */


INSTANTIATE_TEST_CASE_P(
    KeysDataSinglesOptions,
    KeysDataSingles,
    key_generator
);

INSTANTIATE_TEST_CASE_P(
    KeysDataPairsOptions,
    KeysDataPairs,
    testing::Combine(
        key_generator,
        key_generator
    )
);

INSTANTIATE_TEST_CASE_P(
    KeysDataTriplesOptions,
    KeysDataTriples,
    testing::Combine(
        key_generator,
        key_generator,
        key_generator
    )
);

INSTANTIATE_TEST_CASE_P(
    KeysDataQuadsOptions,
    KeysDataQuads,
    testing::Combine(
        key_generator,
        key_generator,
        key_generator,
        key_generator
    )
);


#endif  // __FIXTURES_KEYS_DATA_H__
