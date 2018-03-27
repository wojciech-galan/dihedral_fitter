#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import math
from dihedral_fitter.src.lib import *


# class TestRyckaertBellemanFunction(unittest.TestCase):
#     def test_zero_angles(self):
#         self.assertAlmostEqual(ryckaert_bellemans_function([1, 2], [0, 0]), -2)
#
#     def test_zero_coefs(self):
#         self.assertAlmostEqual(ryckaert_bellemans_function([0, 0], [0, math.pi / 2]), 0)
#
#     def test_simple_data(self):
#         self.assertAlmostEqual(ryckaert_bellemans_function([1, 2], [0, math.pi / 4, math.pi / 2]), 1 - math.sqrt(2))
# TODo fix tests for ryckaert-belleman


class TestRMSD(unittest.TestCase):
    def test_same_arrays(self):
        self.assertAlmostEqual(rmsd(np.array(range(5)), np.array(range(5))), 0)

    def test_different_arrays(self):
        self.assertAlmostEqual(rmsd(np.array([0, 1, 2, 3]), np.array([0, 1, 2, 4])), 0.5)

    def test_different_negative_numbers(self):
        self.assertAlmostEqual(rmsd(np.array([0, -1, -2, -3]), np.array([0, -1, -2, -4])), 0.5)


class TestRMSDForMultipleArrays(unittest.TestCase):
    def setUp(self):
        self.array_3_2 = np.arange(6).reshape((3, 2))
        self.array_2_2 = np.arange(4).reshape((2, 2))

    def test_same_data_one_array(self):
        self.assertAlmostEqual(rmsd_for_multiple_arrays([np.arange(5)], [np.arange(5)]), 0)

    def test_same_data_two_arrays(self):
        self.assertAlmostEqual(
            rmsd_for_multiple_arrays([self.array_3_2, self.array_2_2], [self.array_3_2, self.array_2_2]), 0)

    def test_one_array(self):
        self.assertAlmostEqual(rmsd_for_multiple_arrays([self.array_3_2], [np.zeros((3, 2))]), math.sqrt(55 / 6))

    def test_two_arrays(self):
        self.assertAlmostEqual(
            rmsd_for_multiple_arrays([self.array_3_2, self.array_2_2], [np.ones((3, 2)), np.ones((2, 2))]),
            math.sqrt(3.7))

    def test_same_length(self):
        with self.assertRaises(AssertionError):
            rmsd_for_multiple_arrays([self.array_3_2, self.array_2_2], [np.ones((3, 2))])

    def test_second_dimension_differs(self):
        with self.assertRaises(AssertionError):
            rmsd_for_multiple_arrays([self.array_3_2, np.arange(6).reshape((2, 3))], [np.ones((3, 2)), np.ones((2, 3))])


if __name__ == '__main__':
    unittest.main()
