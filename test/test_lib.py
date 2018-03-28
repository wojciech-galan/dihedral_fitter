#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import math
from dihedral_fitter.src.lib import *


class TestRyckaertBellemansFunction(unittest.TestCase):
    def test_zero_angles(self):
        self.assertListEqual(ryckaert_bellemans_function([1, 2], [0, 0]), [-1, -1])

    def test_zero_coefs(self):
        self.assertListEqual(ryckaert_bellemans_function([0, 0], [0, math.pi / 2]), [0, 0])

    def test_simple_data(self):
        res = ryckaert_bellemans_function([1, 2], [0, math.pi / 4, math.pi / 2])
        proper_res = [-1, 1 - math.sqrt(2), 1]
        for i in range(len(res)):
            self.assertAlmostEqual(res[i], proper_res[i])


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


class TestSubstractListsOfArrays(unittest.TestCase):
    def setUp(self):
        self.array_3_2 = np.arange(6).reshape((3, 2))
        self.array_2_2 = np.arange(4).reshape((2, 2))

    def test_different_lengths(self):
        with self.assertRaises(AssertionError):
            substract_lists_of_arrays([self.array_3_2, self.array_2_2], [np.ones((3, 2))])

    def test_different_shapes(self):
        with self.assertRaises(AssertionError):
            substract_lists_of_arrays([self.array_3_2, self.array_2_2], [np.ones((3, 2)), np.ones((1, 4))])

    def test_data(self):
        proper_res = [np.array([-1, 0, 1, 2, 3, 4]).reshape((3, 2)), self.array_2_2]
        subtraction_result = substract_lists_of_arrays([self.array_3_2, self.array_2_2],
                                                       [np.ones((3, 2)), np.zeros((2, 2))])
        self.assertTrue(all(np.allclose(proper_res[i], subtraction_result[i]) for i in range(len(proper_res))))


if __name__ == '__main__':
    unittest.main()
