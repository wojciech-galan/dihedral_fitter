#! /usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from dihedral_fitter.src.energy_unit import EnergyUnitConverter


class TestEnergyUnitConverter(unittest.TestCase):

    def setUp(self):
        self.converter = EnergyUnitConverter(4.0)

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

    def test_get_energy_in_unit_kj_per_mol(self):
        self.assertAlmostEqual(4.0, self.converter.get_energy_in_unit('kJ/mol'))

    def test_get_energy_in_unit_kcal_per_mol(self):
        self.assertAlmostEqual(0.95538358, self.converter.get_energy_in_unit('kcal/mol'))

    def test_get_energy_in_unit_unsupported(self):
        with self.assertRaises(NotImplementedError):
            self.converter.get_energy_in_unit('cal/mol')


if __name__ == '__main__':
    unittest.main()
