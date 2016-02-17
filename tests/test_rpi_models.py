#/usr/bin/python

# test_rpi_models.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This module tests the detection of all RaspberryPI models
#

import unittest

import sys
sys.path.append('../')

import kano.utils
from kano.utils import get_rpi_model as getrpi


class TestRaspberryPIModels(unittest.TestCase):

    def test_model_A(self):
        modela='RPI/A'
        self.assertIn(getrpi('0007'), modela)
        self.assertIn(getrpi('0008'), modela)
        self.assertIn(getrpi('0009'), modela)

    def test_module_a_plus(self):
        self.assertEqual(getrpi('0012'), 'RPI/A+')

    def test_model_B(self):
        modelb='RPI/B'

        self.assertIn('Beta', getrpi('Beta'))

        self.assertEqual(getrpi('0002'), modelb)
        self.assertEqual(getrpi('0003'), modelb)
        self.assertEqual(getrpi('0004'), modelb)
        self.assertEqual(getrpi('0005'), modelb)
        self.assertEqual(getrpi('0006'), modelb)

        self.assertEqual(getrpi('000D'), modelb)
        self.assertEqual(getrpi('000E'), modelb)
        self.assertEqual(getrpi('000F'), modelb)

    def test_model_B_plus(self):
        self.assertEqual(getrpi('0010'), 'RPI/B+')
        self.assertEqual(getrpi('0013'), 'RPI/B+')

    def test_compute_module(self):
        self.assertEqual(getrpi('0011'), 'Compute Module')

    def test_model_rpi2(self):
        self.assertEqual(getrpi('A01041'), 'RPI/2/B')
        self.assertEqual(getrpi('A21041'), 'RPI/2/B')

    def test_model_zero(self):
        self.assertEqual(getrpi('900092'), 'RPI/Zero')


class TestRaspberryPIOverclocked(unittest.TestCase):

    def test_overclocked_models(self):
        for m in range(7, 9):
            model_name = getrpi('100{}'.format(m)).split()
            self.assertIn ('RPI/A', model_name)

        # Model A+ overclocked
        model_aplus=getrpi('1012')
        self.assertIn ('RPI/A+', model_aplus)

        expected_model_b='RPI/B'
        for m in range(2, 6):
            model_name = getrpi('100{}'.format(m)).split()
            self.assertIn (expected_model_b, model_name)

        self.assertEqual(getrpi('100D'), expected_model_b)
        self.assertEqual(getrpi('100E'), expected_model_b)
        self.assertEqual(getrpi('100F'), expected_model_b)

        self.assertEqual(getrpi('1010'), 'RPI/B+')

        self.assertEqual(getrpi('1011'), 'Compute Module')

class TestModelAsserters(unittest.TestCase):

    def test_models_asserts(self):
        self.assertTrue (kano.utils.is_model_a('0007'))
        self.assertTrue (kano.utils.is_model_b('0004'))
        self.assertTrue (kano.utils.is_model_b_plus('0010'))
        self.assertTrue (kano.utils.is_model_2_b('0xA01041'))

class TestModelAsserters(unittest.TestCase):

    def test_unknown(self):
        self.assertIn ('unknown', getrpi('ABCD'))


if __name__ == '__main__':
    unittest.main()
