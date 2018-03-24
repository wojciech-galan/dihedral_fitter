#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import numpy as np
from dihedral_fitter.src.optimizer import *


class TestRMSD(unittest.TestCase):

    def test_same_arrays(self):
        self.assertAlmostEqual(rmsd(np.array(range(5)), np.array(range(5))), 0)

    def test_different_arrays(self):
        self.assertAlmostEqual(rmsd(np.array([0, 1, 2, 3]), np.array([0, 1, 2, 4])), 0.5)

    def test_different_negative_numbers(self):
        self.assertAlmostEqual(rmsd(np.array([0, -1, -2, -3]), np.array([0, -1, -2, -4])), 0.5)



if __name__ == '__main__':
    unittest.main()
