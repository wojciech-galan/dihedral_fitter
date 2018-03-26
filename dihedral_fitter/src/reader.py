#! /usr/bin/python
# -*- coding: utf-8 -*-

import abc
import os
from typing import Any
from dihedral_fitter.src.energy_unit import EnergyUnitConverter


class FileReader(abc.ABC):
    @abc.abstractmethod
    def __init__(self, f_path: str):
        FileReader._check_path(f_path)
        super().__init__()
        self.path = f_path

    @staticmethod
    def _check_path(f_path: str) -> None:
        assert type(f_path) is str
        assert os.path.exists(f_path) and os.path.isfile(f_path)

        # @abc.abstractmethod
        # def get_content(self) -> Any:
        #     pass


class EnergyFileReader(FileReader):
    @abc.abstractmethod
    def __init__(self, f_path: str):
        super().__init__(f_path)


class SimpleEnergyReader(EnergyFileReader):
    """Assumes that the file contains only energy values, one per line"""

    def __init__(self, f_path: str, unit: str = 'kJ/mol'):
        super().__init__(f_path)
        self.unit = unit
        self.energies = []
        with open(f_path) as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    self.energies.append(EnergyUnitConverter(float(stripped), unit))

                    # def get_content(self):
                    #     pass
