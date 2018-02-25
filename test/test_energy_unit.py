#! /usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from dihedral_fitter.src.energy_unit import EnergyUnitConverter


class TestEnergyUnitConverter(unittest.TestCase):
    """Just to be sure that the tests are run from the dir containing test_data dir"""

    def test_creation_wrong_units(self):
        with self.assertRaises(AssertionError):
            EnergyUnitConverter(5, 'j/mol')

    def test_creation_wrong_value_type(self):
        with self.assertRaises(AssertionError):
            EnergyUnitConverter([])

    def test_creation_float_kj(self):
        self.assertEqual(EnergyUnitConverter(5.), 5)

    def test_creation_float_kcal(self):
        self.assertAlmostEqual(EnergyUnitConverter(5., 'kcal/mol'), 20.934, places=3)

    def test_creation_int_kj(self):
        self.assertEqual(EnergyUnitConverter(5), 5)

    def test_creation_int_kcal(self):
        self.assertAlmostEqual(EnergyUnitConverter(5, 'kcal/mol'), 20.934, places=3)


if __name__ == '__main__':
    unittest.main()
