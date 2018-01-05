/**
 * test_hotkeys.cpp
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
 *
 * Tests for the basic hotkey functionality
 *
 */


// Test framework
#include "gtest/gtest.h"
#include "gmock/gmock.h"

// Lib dependencies
#include <map>
#include <vector>
#include <algorithm>

// Stubs
#include "linux/input.h"

// Fixtures
#include "fixtures/key.h"
#include "fixtures/keys_data.h"
#include "fixtures/mock_ioctl.h"

// Functions to test
#include "hotkeys.h"
#include "hotkeys.cpp"


/**
 * add_keymask() Tests
 */


template<typename T>
void KeysData<T>::test_add_mask()
{
    std::map<uint8_t, std::vector<Key>> key_byte_map;

    for (auto key : this->keys) {
        EXPECT_TRUE(add_keymask(this->mask, sizeof this->mask, key.key_bit));
        key_byte_map[key.byte].push_back(key);
    }

    for (int i = 0; i < sizeof this->mask; i++) {
        int val = 0;

        for (auto key : key_byte_map[i]) {
            val |= key.val;
        }

        EXPECT_EQ(this->mask[i], val);
    }
}


TEST_P(KeysDataSingles, test_add_keymask_singles) {
    this->test_add_mask();
}


TEST_P(KeysDataPairs, test_add_keymask_pairs) {
    this->test_add_mask();
}


TEST_P(KeysDataQuads, test_add_keymask_quads) {
    this->test_add_mask();
}


/**
 * mask_match() Tests
 */


template<typename T>
void KeysData<T>::test_mask_match()
{
    // We expect this to be called only for even numbers of parameters so divide
    // keys in half

    const std::size_t len = this->keys.size() / 2;

    std::vector<Key> keys_buff(this->keys.begin(), this->keys.begin() + len);
    std::sort(keys_buff.begin(), keys_buff.end());

    std::vector<Key> keys_mask(this->keys.begin() + len, this->keys.end());
    std::sort(keys_mask.begin(), keys_mask.end());

    bool are_keys_equal = true;

    auto buff_it = keys_buff.cbegin();
    for (auto mask_it = keys_mask.cbegin(); mask_it != keys_mask.cend(); ++mask_it, ++buff_it) {
        if (*mask_it != *buff_it) {
            are_keys_equal = false;
            break;
        }
    }

    uint8_t test_buff[16];
    memset(test_buff, 0, sizeof test_buff);

    for (auto key : keys_buff) {
        add_keymask(test_buff, sizeof test_buff, key.key_bit);
    }

    for (auto key : keys_mask) {
        add_keymask(this->mask, sizeof this->mask, key.key_bit);
    }

    // Only match if all the keys are pairwise equal
    EXPECT_EQ(
        mask_match(test_buff, sizeof test_buff, this->mask, sizeof this->mask),
        are_keys_equal
    );
}


TEST_P(KeysDataPairs, test_mask_match_pairs) {
    this->test_mask_match();
}


TEST_P(KeysDataQuads, test_mask_match_quads) {
    this->test_mask_match();
}


/**
 * are_keys_pressed() Tests
 */


/**
 * Combinations of Ctrl + Alt to trigger. Currently requires exactly 2 key
 * presses, of which one key has to be the Lef Alt key and the other can be
 * either the Left or Right Ctrl key.
 */
#define CTRL_ALT_COMBO_1    KEY_LEFTCTRL, KEY_LEFTALT
#define CTRL_ALT_COMBO_2    KEY_RIGHTCTRL, KEY_LEFTALT


#define CTRL_ALT_COMBO \
    testing::UnorderedElementsAre(CTRL_ALT_COMBO_1), \
    testing::UnorderedElementsAre(CTRL_ALT_COMBO_2)

#define CTRL_ALT_1_COMBO \
    testing::UnorderedElementsAre(KEY_1, CTRL_ALT_COMBO_1), \
    testing::UnorderedElementsAre(KEY_1, CTRL_ALT_COMBO_2)

#define CTRL_ALT_7_COMBO \
    testing::UnorderedElementsAre(KEY_7, CTRL_ALT_COMBO_1), \
    testing::UnorderedElementsAre(KEY_7, CTRL_ALT_COMBO_2)


std::vector<Key> strip_duplicates(std::vector<Key> keys)
{
    std::sort(keys.begin(), keys.end());
    std::vector<Key> unique_keys;

    Key prev_key;

    for (auto key : keys) {
        if (key == prev_key)
            continue;

        prev_key = key;
        unique_keys.push_back(key);
    }

    return unique_keys;
}



template<typename T>
void MockIoctl<T>::test_check_hotkeys()
{
    Hotkey hotkey = check_hotkeys(0, false);
    auto unique_keys = strip_duplicates(this->keys);

    switch (hotkey) {
    case CTRL_ALT:
        EXPECT_THAT(unique_keys, testing::AnyOf(CTRL_ALT_COMBO));
        break;
    case CTRL_ALT_1:
        EXPECT_THAT(unique_keys, testing::AnyOf(CTRL_ALT_1_COMBO));
        break;
    case CTRL_ALT_7:
        EXPECT_THAT(unique_keys, testing::AnyOf(CTRL_ALT_7_COMBO));
        break;
    case NO_HOTKEY:
        EXPECT_THAT(unique_keys, testing::Not(testing::AnyOf(CTRL_ALT_COMBO)));
        EXPECT_THAT(unique_keys, testing::Not(testing::AnyOf(CTRL_ALT_1_COMBO)));
        EXPECT_THAT(unique_keys, testing::Not(testing::AnyOf(CTRL_ALT_7_COMBO)));
        break;
    default:
        FAIL() << "check_hotkeys() should return one of the above.";
        break;
    }
}


TEST_P(MockIoctlSingles, test_check_hotkeys_singles) {
    this->test_check_hotkeys();
}


TEST_P(MockIoctlPairs, test_check_hotkeys_pairs) {
    this->test_check_hotkeys();
}


TEST_P(MockIoctlTriples, test_check_hotkeys_triples) {
    this->test_check_hotkeys();
}


TEST_P(MockIoctlQuads, test_check_hotkeys_quads) {
    this->test_check_hotkeys();
}
