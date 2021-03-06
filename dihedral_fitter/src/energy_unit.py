#! /usr/bin/python
# -*- coding: utf-8 -*-
from typing import Union

possible_units = {'kJ/mol', 'kcal/mol'}


class EnergyUnitConverter(float):
    """
    Converts energy units. Internally keeps all units in kJ/mol
    """
    multipliers = {
        'kcal/mol': 4.1868 # international calorie
    }
    def __new__(cls, value: Union[int, float], unit: str = 'kJ/mol'):
        """
        EnergyUnitConverter inherits from immutable type (float), so it needs a constructor
        :param value: value of the object
        :param unit: energy unit
        :return: new EnergyUnitConverter object
        """
        assert type(value) in [int, float]
        assert unit in possible_units
        if unit != 'kJ/mol':
            value = float(value) * cls.multipliers[unit]
        return float.__new__(cls, value)

    def __init__(self, value: Union[int, float], unit: str = 'kJ/mol'):
        self.unit = 'kJ/mol'

    def get_energy_in_unit(self, unit: str = 'kJ/mol') -> float:
        if unit == 'kJ/mol':
            return float(self)
        try:
            return self / self.__class__.multipliers[unit]
        except KeyError:
            raise NotImplementedError(
                "The method does't work for {0}. Only {1} are supported".format(unit, ', '.join(possible_units)))


if __name__ == '__main__':
    print(EnergyUnitConverter(5) == 5)
    print(EnergyUnitConverter(5).__dict__)
    print(type(EnergyUnitConverter(5) + 1))
    print(type(EnergyUnitConverter(5)))
    print(EnergyUnitConverter(5).get_energy_in_unit('kcal/mol'))
