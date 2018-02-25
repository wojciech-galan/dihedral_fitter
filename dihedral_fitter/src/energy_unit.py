#! /usr/bin/python
# -*- coding: utf-8 -*-
from typing import Union

possible_units = set(['kJ/mol', 'kcal/mol'])
multipliers = {
    'kcal/mol': 4.1868
}


class EnergyUnitConverter(float):
    """
    Converts energy units. Internally keeps all units in kJ/mol
    """

    def __new__(cls, value: Union[int, float], unit: str = 'kJ/mol'):
        assert type(value) in [int, float]
        assert unit in possible_units
        if unit != 'kJ/mol':
            value = float(value) * multipliers[unit]
        return float.__new__(cls, value)

    def __init__(self, value: Union[int, float, str], unit: str = 'kJ/mol'):
        self.unit = 'kJ/mol'

    def get_energy_in_unit(self, unit: str = 'kJ/mol') -> float:
        if unit == 'kJ/mol':
            return float(self)
        try:
            return self / multipliers[unit]
        except KeyError:
            raise NotImplementedError(
                "The method does't work for {0}. Only {1} are supported".format(unit, ', '.join(possible_units)))


if __name__ == '__main__':
    print(EnergyUnitConverter(5) == 5)
    print(EnergyUnitConverter(5).__dict__)
    print(type(EnergyUnitConverter(5) + 1))
    print(type(EnergyUnitConverter(5)))
    print(EnergyUnitConverter(5).get_energy_in_unit('kcal/mol'))
