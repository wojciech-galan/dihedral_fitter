#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import os
from dihedral_fitter.src.reader import *
from dihedral_fitter.src.energy_unit import EnergyUnitConverter


class TestProperDirectory(unittest.TestCase):
    """Just to be sure that the tests are run from the directory containing test_data subdirectory"""

    def test_proper_dir(self):
        self.assertEqual(os.path.basename(os.getcwd()), 'dihedral_fitter')


class TestFileReader(unittest.TestCase):
    def test_object_creation(self):
        with self.assertRaises(TypeError):
            FileReader('test_data')

    def test_path_is_string(self):
        with self.assertRaises(AssertionError):
            FileReader._check_path([])

    def test_file_exists(self):
        with self.assertRaises(AssertionError):
            FileReader._check_path('/dev/null/blah')

    def test_file_is_a_regular_file(self):
        with self.assertRaises(AssertionError):
            FileReader._check_path('test_data')


class TestFileReader(unittest.TestCase):
    def test_object_creation(self):
        with self.assertRaises(TypeError):
            FileReader(os.path.join('test_data', 'reader', 'test.simple_energy'))


if __name__ == '__main__':
    unittest.main()
