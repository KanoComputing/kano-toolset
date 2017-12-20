# test.py
#
# Copyright (C) 2016-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Unit test for luon.py
#
import pytest
import unittest

import json
import os
import sys
from kano.utils.lua import luon
from random import randint, choice, seed
import math
seed(500)

MAX_TESTS = 1000

MAX_TEST_INT = 16777216


class tfilenames:
    def __init__(self, num):
        self.num = num

    @property
    def lua_test_file(self):
        return "temp/t_{}.lua".format(self.num)

    @property
    def lua_test_cmp(self):
        return "temp/t_{}.json".format(self.num)

    @property
    def lua_out_json(self):
        return "temp/l_{}.json".format(self.num)

    @property
    def lua_out2_json(self):
        return "temp/l2_{}.json".format(self.num)




def random_value(use_float=True, max_depth=5, max_items=1000):
    '''
    Generate a random python value suitable for converting to json/luon

    Caveats:
    * limited integer range, because lua converts large integers to float
    * uses heuristic to check whether floats are converted correctly,
      and knowledge of whether orignal value was int/float

    '''
    def r_int():
        return randint(-MAX_TEST_INT+1, MAX_TEST_INT)

    def r_bool():
        return choice([True, False])

    def r_float():
        if r_bool():
            exp = randint(-100, 100)
        else:
            exp = randint(0, 10)

        mant = randint(-65536, 65536)

        return choice([-1, 1])*mant*math.pow(2, exp)

    def r_char_ascii():
        return chr(randint(0, 127))

    def r_len():
        return randint(0, min(max_items, choice([3, 10, 100, 1000])))

    def r_char_unicode():
        # don't test code points in the reserved 'high surrogate' area
        return unichr(randint(0, choice([256, 0xD7FF])))

    def r_str(r_char=r_char_ascii):
        return ''.join([r_char() for i in xrange(r_len())])

    def r_unicode():
        return r_str(r_char_unicode)

    def r_array():
        l = r_len()

        return [random_value(use_float, max_depth-1, max_items/l)
                for i in xrange(l)]

    def r_dict():
        res = {}
        l = r_len()

        for i in xrange(l):
            res[choice([r_str, r_unicode])()] = random_value(
                use_float, max_depth-1, max_items / l)

    if max_depth > 1:
        cl = [r_int, r_bool, r_str,
              r_unicode, r_array, r_dict]
    else:
        cl = [r_int, r_bool, r_str,
              r_unicode]

    if use_float:
        cl.append(r_float)

    return choice(cl)()


# place to set breakpoints
def fail():
    return False


# ensure failure always goes via fail()
def res(b):
    if not b:
        fail()
    return b


# from python 3.5 doc (via http://stackoverflow.com/questions/5595425/what-is-the-best-way-to-compare-floats-for-almost-equality-in-python)
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def compare(x, y):
    '''
    Compare two python values, with fuzzy float equality
    '''
    if isinstance(x, dict):
        if not isinstance(y, dict):
            print "difference: ", x, y
            return fail()
        for k in x.keys():
            if k not in y:
                print "missing key", k
                return fail()
            if compare(x[k], y[k]):
                continue
            return fail()
        return True
    if isinstance(x, list):
        if not isinstance(y, list):
            print "difference: ", x, y
            return fail()
        if not len(x) == len(y):
            print "difference: ", x, y
            return fail()
        for i in xrange(len(x)):
            if compare(x[i], y[i]):
                continue
            return fail()
        return True

    def icmp(x, y):
        equal = x == y
        if not equal:
            fail()
            print "mismatch: ", x, y
        return res(equal)

    if isinstance(x, bool):
        return res(isinstance(y, bool)) and icmp(x, y)
    if isinstance(x, str) or isinstance(x, unicode):
        return res(isinstance(y, str)or isinstance(y, unicode)) and icmp(x, y)
    if isinstance(x, float) or isinstance(x, int):
        if (isinstance(x, int) or
            math.modf(x)[0] == 0.0) and abs(x) < MAX_TEST_INT:

            # only compare as integers if the original value was an integer
            if not math.modf(y)[0] == 0:
                print " integer/float mismatch", x, y
                return fail()
            return icmp(int(x), int(y))
        equal = isclose(x, y)
        if not equal:
            print "float mismatch: ", x, y
        return res(equal)
    if isinstance(x, type(None)):
        return res(isinstance(y, type(None)))
    else:
        print "Unknown type!: ", type(x)
        return fail()


# test that conversion to lua and back works for
# data 'j'. specifies string or program comparision
def do_test_json(files, j, use_streq):

    # dump j for comparison
    sj = json.dumps(j, indent=4)

    # write lua test data
    with open(files.lua_test_file, "w") as ltf:
        ltf.write(luon.dumps(j))

    # write comparison
    with open(files.lua_test_cmp, "w") as ltc:
        ltc.write(sj)

    # convert lua back
    dirpath = os.path.dirname(luon.__file__)
    rc = os.system("lua -e 'package.path=package.path..\";{}/?.lua\"' {}/lua_to_json.lua ".format(dirpath, dirpath) +
                   files.lua_test_file + " " + files.lua_out_json)

    if rc != 0:
        return (False, "failed to execute")

    # load lua data back
    with open(files.lua_out_json) as lf:
        l = json.load(lf)

    # convert lua data back to json again for string
    # comparison, to avoid worry about formatting
    oj = json.dumps(l, indent=4)
    with open(files.lua_out2_json, "w") as lf2:
        lf2.write(oj)

    # do actual comparison
    if use_streq:
        equal = sj == oj
    else:
        equal = compare(j, l)

    return (equal, "compare")


def run_tests(jfile=None, set_float=True):
    all_succeeded = True
    os.system("mkdir temp")

    if jfile:
        # For rerunning a test, pass its json file as argument

        print "Loading: ", jfile
        with open(jfile) as jf:
            j = json.load(jf)
        success, errmsg = do_test_json(tfilenames('t'),j,int(set_float))
        if not success:
            print "FAILED test {}".format(json.dumps(j))
            all_succeeded = False
        else:
            print "Test passed"
    else:
        for i in xrange(MAX_TESTS):
            files = tfilenames(i)
            # compare in two ways:
            #  * string equality of jsons (without floating values)
            #  * data equality (with fuzzy float compare)

            use_float = choice([True, False])
            
            j = random_value(use_float)
            success, errmsg = do_test_json(files, j, not use_float)

            if not success:
                print "FAILED test {}".format(i)
                os.system(" diff {} {} ".format(files.lua_test_cmp,
                                            files.lua_out2_json))
                all_succeeded = False
                break
            else:
                print "Test {} passed".format(i)

        if all_succeeded:
            print "YAAAY!"
        else:
            print ":-((("
        return all_succeeded


@pytest.mark.lua
class TestLua(unittest.TestCase):
    def test_lua_json(self):
        self.assertTrue(run_tests())

if __name__ == '__main__':
    if len(sys.argv) == 3:
        run_tests(sys.argv[1], sys.argv[2])
    else:
        unittest.main()
