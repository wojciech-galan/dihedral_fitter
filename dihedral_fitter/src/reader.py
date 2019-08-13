#! /usr/bin/python
# -*- coding: utf-8 -*-

import abc
import os
import re
from typing import Any
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


# class YamlEnergyReader(EnergyFileReader):
#     """Assumes the file is in format similar to sample_files/energy.sample.yaml"""
#     def __init__(self, f_path:str):
#         super().__init__(f_path)
#
#     def read(self):
#         with open(self.path) as f:
#             data = yaml.load(f)
#         print(data.keys())
class DihedralContainer(object):

    def __init__(self, data:List[DihedralData]):
        super().__init__()
        self.data = data


class DihedralData(object):

    def __init__(self, energy_unit:str, angle_unit:str, atom_numbers:List[int], energy_for_angle_tuples:List[Tuple[float]]):
        super().__init__()
        self.energy_unit=  energy_unit
        self.angle_unit = angle_unit
        self.atom_numbers = atom_numbers
        self.angles, self.energies  = zip(*energy_for_angle_tuples)


class DihedralType(UserString):

    def __init__(self, string_a: str, atom_numbers: List[str]):
        found = re.search('(\w+-\w+-\w+-\w+)', string_a)
        improper_dihedral_string_error = RuntimeError("Improper dihedral string: {}".format(string_a))
        try:
            group = found.group(1)
        except AttributeError:
            raise improper_dihedral_string_error
        if len(string_a) != len(group):
            raise improper_dihedral_string_error
        super().__init__(DihedralType._alphabetic_order(string_a, atom_numbers))

    @staticmethod
    def _alphabetic_order(string_a: str, atom_numbers: List[str]):
        splitted = string_a.split('-')
        if splitted[-1] < splitted[0]:
            atom_numbers.reverse()
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
    print(DihedralType('OS-CT-CT-CT') == DihedralType('CT-CT-CT-OS'))
    reader = YamlEnergyReader('/home/wojtek/Pobrane/energia_qm.txt')
    reader.read()
