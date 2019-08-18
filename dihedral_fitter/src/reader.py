#! /usr/bin/python
# -*- coding: utf-8 -*-

import abc
import os
import re
import json
import yaml
from typing import Tuple
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


class JsonMapFileReader(FileReader):
    def __init__(self, f_path):
        super().__init__(f_path)

    def read(self):
        with open(self.path) as f:
            content = json.load(f)
        ret_dict = {}
        for k, v in content.items():
            ret_dict[k] = DihedralType(*v)
        return ret_dict


class YamlEnergyReader(FileReader):
    def __init__(self, f_path: str):
        super().__init__(f_path)

    def read(self):
        with open(self.path) as f:
            data = yaml.safe_load(f)
        energy_unit = data[-1]['energy_unit']
        angle_unit = data[-1]['angle_unit']
        assert angle_unit == 'degree'  # todo support for radian
        energies = [
            {'energy': EnergyUnitConverter(energy_dict['energy'], energy_unit), 'dihedrals': energy_dict['dihedrals']}
            for energy_dict in data[:-1]]
        return energies


class DihedralData(object):
    def __init__(self, energy_unit: str, angle_unit: str, atom_numbers: List[int],
                 energy_for_angle_tuples: List[Tuple[float]]):
        super().__init__()
        self.energy_unit = energy_unit
        self.angle_unit = angle_unit
        self.atom_numbers = atom_numbers
        self.angles, self.energies = zip(*energy_for_angle_tuples)


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
        ordered_atoms_string, ordered_atom_numbers = DihedralType._alphabetic_order(string_a, atom_numbers)
        super().__init__(ordered_atoms_string)
        self.atom_numbers = ordered_atom_numbers

    @staticmethod
    def _alphabetic_order(string_a: str, atom_numbers: List[str]):
        splitted = string_a.split('-')
        if splitted[-1] < splitted[0]:
            atom_numbers.reverse()
            return '-'.join(reversed(splitted)), atom_numbers
        return string_a, atom_numbers

    def equal_dihedral_type(self, other):
        return isinstance(other, self.__class__) and self.data == other.data

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


if __name__ == '__main__':
    print(DihedralType('OS-CT-CT-CT', []))
    print(DihedralType('OS-CT-CT-CT', []) == DihedralType('CT-CT-CT-OS', []))
    reader = JsonMapFileReader("/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/plik1.json")
    mapping = reader.read()
    reader = YamlEnergyReader("/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/E_zRB.yaml")
    energies = reader.read()
    print(energies[-1])
    # reader = YamlEnergyReader('/home/wojtek/Pobrane/energia_qm.txt')
    # reader.read()
