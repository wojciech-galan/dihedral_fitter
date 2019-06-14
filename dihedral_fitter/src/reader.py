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

    def __init__(self, f_path: str):
        super().__init__(f_path)

    def read(self):
        with open(self.path) as f:
            data = yaml.load(f)
        return Energies(data['energy unit'], data['angle unit'], data['energies'])


class Energies(object):
    def __init__(self, energy_unit: str, angle_unit: str, energies: List[Dict[str, Any]]):
        super().__init__()
        self.energy_unit = energy_unit
        self.energy_unit = angle_unit
        num_of_entries = len(energies[0]["contribution to the particle's energy computed for given angle"])
        num_of_dihedrals = len(energies)
        print(energies[0]["contribution to the particle's energy computed for given angle"])
        print(len(energies[0]["contribution to the particle's energy computed for given angle"]))
        # zdarza się, że mam dwie wartości energii dla tego samego kąta. Wtedy biorę niższa energię.
        print([len(x["contribution to the particle's energy computed for given angle"]) == num_of_entries for x in energies])
        print([len(x["contribution to the particle's energy computed for given angle"]) for x in energies])
        assert all(len(x["contribution to the particle's energy computed for given angle"]) == num_of_entries for x in energies)
        self.energies = np.empty((num_of_dihedrals, num_of_entries))
        self.angles = np.empty((num_of_dihedrals, num_of_entries))
        self.dihedral_energies_metadata = []
        for i, entry in enumerate(energies):
            self.angles[i] = list(entry['energy for given angle'].keys)
            self.energies[i] = list(entry['energy for given angle'].values)
            self.dihedral_energies_metadata.append(entry['atom numbers'], entry['dihedral_type'])


class DihedralEnergiesMetadata(object):
    def __init__(self, atom_numbers: List[str], dihedral_type: str):
        super().__init__()
        self.atom_numbers = atom_numbers
        self.dihedral_type = DihedralType(dihedral_type, self.atom_numbers)


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
    reader = YamlEnergyReader('/home/wojtek/Pobrane/energia_qm.txt')
    reader.read()
