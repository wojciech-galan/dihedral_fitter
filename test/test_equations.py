#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import math
from dihedral_fitter.src.equations import *

class TestRyckaertBellemanFunction(unittest.TestCase):

    def test_zero_angles(self):
        self.assertAlmostEqual(ryckaert_bellemans_function([1, 2], [0, 0]), -2)

    def test_zero_coefs(self):
        self.assertAlmostEqual(ryckaert_bellemans_function([0, 0], [0, math.pi/2]), 0)

    def test_simple_data(self):
        self.assertAlmostEqual(ryckaert_bellemans_function([1, 2], [0, math.pi/4, math.pi/2]), 1-math.sqrt(2))


if __name__ == '__main__':
       unittest.main()
