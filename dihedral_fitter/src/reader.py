#! /usr/bin/python
# -*- coding: utf-8 -*-

import abc
import os
import re
import json
import yaml
from typing import Dict
from typing import List
from typing import Union
from collections import UserString
from frozendict import frozendict
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
            ret_dict[int(k)] = DihedralType(*v)
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
        energies = [{'energy': EnergyUnitConverter(energy_dict['energy'], energy_unit).get_energy_in_unit('kJ/mol'),
                     'dihedrals': energy_dict['dihedrals']} for energy_dict in data[:-1]]
        return energies


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
        self.atom_numbers = tuple(ordered_atom_numbers)

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

    def __hash__(self):
        return 7 * hash(self.data) + 11 * hash(self.atom_numbers)


class DihedralDataContainer(object):
    """
    Merges energies with metadata
    """

    def __init__(self, energies_data: List[Dict[str, Union[float, Dict[int, float]]]],
                 angle_mapping: Dict[int, DihedralType]):
        """
        Creates
        :param energies_data: list of dictionaries containing energies (in kj/mol) for given angles (in degrees)
                example dictionary: {'energy': 19.1844, 'dihedrals': {0: 175.995, 1: 102.256, 2: -179.726, 3: 81.27}}
        :param angle_mapping: translation between angle number and DihedralType
        """
        super().__init__()
        self.data = {}
        dihedral_nums_groupped_by_string = self.__group_dihedrals(angle_mapping)
        print(dihedral_nums_groupped_by_string)
        for energy_data in energies_data:
            data_for_given_energy = {}
            for dihedral_string, dihetral_numbers in dihedral_nums_groupped_by_string.items():
                data_for_given_energy[dihedral_string] = tuple([energy_data['dihedrals'][dihetral_number] for dihetral_number in dihetral_numbers])
            self.data[frozendict(data_for_given_energy)] = energy_data['energy']

    @staticmethod
    def __group_dihedrals(angle_mapping: Dict[int, DihedralType]) -> Dict[str, List[int]]:
        i = 0
        ret_dict = {}
        angle_mapping_items = list(angle_mapping.items())
        while i < len(angle_mapping_items):
            angle_numbers = [angle_mapping_items[i][0]]
            dihedral_type = angle_mapping_items[i][1]
            dihedral_atoms_string = dihedral_type.data
            j = i + 1
            while j < len(angle_mapping_items):
                dihedral_2_type = angle_mapping_items[j][1]
                if dihedral_atoms_string == dihedral_2_type.data:
                    angle_numbers.append(angle_mapping_items[j][0])
                    del angle_mapping_items[j]
                else:
                    j += 1
            ret_dict[dihedral_atoms_string] = angle_numbers
            i += 1
        return ret_dict

    def items(self):
        return self.data.items()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        return self.data[item]


if __name__ == '__main__':
    print(DihedralType('OS-CT-CT-CT', []))
    print(DihedralType('OS-CT-CT-CT', []) == DihedralType('CT-CT-CT-OS', []))
    reader = JsonMapFileReader("/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/plik1.json")
    mapping = reader.read()
    reader = YamlEnergyReader("/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/E_zRB.yaml")
    energies = reader.read()
    print(energies[-1])
    print(mapping)
    # DihedralData(energies[-1]['dihedrals'], mapping)
    for k, v in DihedralDataContainer(energies, mapping).items():
        print(len(k), k)
        print(v)
        raise
