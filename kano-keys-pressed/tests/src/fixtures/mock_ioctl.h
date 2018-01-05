/**
 * mock_ioctl.h
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
 *
 * Fixtures which provide a parameterised set of keys which mock ioctl calls to
 * retrieve them
 *
 */


#ifndef __FIXTURES_MOCK_IOCTL_H__
#define __FIXTURES_MOCK_IOCTL_H__


#include "fixtures/keys_data.h"
#include "stubs/sys/ioctl.h"


/**
 * Mocks ioctl(..., EVIOCGKEY(), ...) calls to provide a selection of values
 * supplied by the parameters for use in a test function
 */
template <typename T>
class MockIoctl : public KeysData<T>
{
    public:
        virtual void SetUp()
        {
            this->load_keys(this->GetParam());
            memset(this->mask, 0, sizeof this->mask);
            ioctl_keys = this->keys;
        }
        void test_check_hotkeys();
};


/**
 * Typedefs for each of these template specializations so that they can be used
 * with INSTANTIATE_TEST_CASE_P's rudimentary #define
 */


typedef class MockIoctl<Key> MockIoctlSingles;
typedef class MockIoctl<std::tuple<Key, Key>> MockIoctlPairs;
typedef class MockIoctl<std::tuple<Key, Key, Key>> MockIoctlTriples;
typedef class MockIoctl<std::tuple<Key, Key, Key, Key>> MockIoctlQuads;


/**
 * Register data for each MockIoctl specialization
 */


INSTANTIATE_TEST_CASE_P(
    MockIoctlSinglesOptions,
    MockIoctlSingles,
    key_generator
);

INSTANTIATE_TEST_CASE_P(
    MockIoctlPairsOptions,
    MockIoctlPairs,
    testing::Combine(
        key_generator,
        key_generator
    )
);

INSTANTIATE_TEST_CASE_P(
    MockIoctlTriplesOptions,
    MockIoctlTriples,
    testing::Combine(
        key_generator,
        key_generator,
        key_generator
    )
);

INSTANTIATE_TEST_CASE_P(
    MockIoctlQuadsOptions,
    MockIoctlQuads,
    testing::Combine(
        key_generator,
        key_generator,
        key_generator,
        key_generator
    )
);


#endif  // __FIXTURES_MOCK_IOCTL_H__
