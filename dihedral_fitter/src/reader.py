#! /usr/bin/python
# -*- coding: utf-8 -*-

import abc
import os
import re
import yaml
import numpy as np
from typing import Any
from typing import Dict
from typing import List
from collections import UserString
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
        self._path = f_path


class YamlEnergyReader(EnergyFileReader):
    """Assumes the file is in format similar to sample_files/energy.sample.yaml"""
    def __init__(self, f_path:str):
        super().__init__(f_path)

    def read(self):
        with open(self.path) as f:
            data = yaml.load(f)
        print(data.keys())


class DihedralEnergies(object):

    def __init__(self, energy_unit:str, angle_unit:str, energies:List[Dict[str, Any]]):
        super().__init__()
        self.energy_unit=  energy_unit
        self.energy_unit = angle_unit



class DihedralType(UserString):

    def __init__(self, string_a:str):
        found = re.search('([a-zA-Z]+-[a-zA-Z]+-[a-zA-Z]+-[a-zA-Z]+)', string_a)
        improper_dihedral_string_error = RuntimeError("Improper dihedral string: {}".format(string_a))
        try:
            group = found.group(1)
        except AttributeError:
            raise improper_dihedral_string_error
        if len(string_a) != len(group):
            raise improper_dihedral_string_error
        super().__init__(DihedralType._alphabetic_order(string_a))

    @staticmethod
    def _alphabetic_order(string_a:str):
        splitted = string_a.split('-')
        if splitted[-1] < splitted[0]:
            return '-'.join(reversed(splitted))
        return string_a

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

if __name__ == '__main__':
    print(DihedralType('OS-CT-CT-CT'))
    print(DihedralType('OS-CT-CT-CT')==DihedralType('CT-CT-CT-OS'))
    reader = YamlEnergyReader('/home/wojtek/Pobrane/energia_qm.txt')
    reader.read()
