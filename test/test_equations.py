#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import math
from dihedral_fitter.src.equations import *


class TestRyckaertBellemanFunction(unittest.TestCase):
    def test_zero_angles(self):
        self.assertAlmostEqual(ryckaert_bellemans_function([1, 2], [0, 0]), -2)

    def test_zero_coefs(self):
        self.assertAlmostEqual(ryckaert_bellemans_function([0, 0], [0, math.pi / 2]), 0)

    def test_simple_data(self):
        self.assertAlmostEqual(ryckaert_bellemans_function([1, 2], [0, math.pi / 4, math.pi / 2]), 1 - math.sqrt(2))


class TestRMSD(unittest.TestCase):
    def test_same_arrays(self):
        self.assertAlmostEqual(rmsd(np.array(range(5)), np.array(range(5))), 0)

    def test_different_arrays(self):
        self.assertAlmostEqual(rmsd(np.array([0, 1, 2, 3]), np.array([0, 1, 2, 4])), 0.5)

    def test_different_negative_numbers(self):
        self.assertAlmostEqual(rmsd(np.array([0, -1, -2, -3]), np.array([0, -1, -2, -4])), 0.5)


if __name__ == '__main__':
    unittest.main()
