#! /usr/bin/python
# -*- coding: utf-8 -*-

import abc
import os
import re
import json
import yaml
import numpy as np
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
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
            ret_dict[int(k)] = DihedralType(*v)
        return ret_dict


class YamlEnergyReader(FileReader):
    def __init__(self, f_path: str):
        super().__init__(f_path)

    def read(self) -> Tuple[Union[float, List[Dict[int, float]]]]:
        with open(self.path) as f:
            data = yaml.safe_load(f)
        energy_unit = data['energy_unit']
        angle_unit = data['angle_unit']
        assert angle_unit == 'degree'  # todo support for radian
        energy = EnergyUnitConverter(data['energy'], energy_unit).get_energy_in_unit('kJ/mol')
        dihedrals = data['dihedrals']
        return energy, dihedrals


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

    def __init__(self, energy:float, dihedrals:List[Dict[int, float]], angle_mapping: Dict[int, DihedralType]):
        """
        Creates
        :param angle_mapping: translation between angle number and DihedralType
        """
        super().__init__()
        self.energy = energy
        # dihedral_nums_groupped_by_string = self.__group_dihedrals(angle_mapping)
        assert all(dihedrals[0].keys() == dihedrals[x].keys() for x in range(1, len(dihedrals)))
        self.dihedrals = self.__create_dihedral_matrix(dihedrals)
        self.dihedral_type_to_row_index_mapping = self.__group_dihedrals(angle_mapping)
        #self.mapping_between_angle_number_and_dihedral_pos_in_matrix = {i:x for i, x in enumerate(dihedrals[0])}


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

    @staticmethod
    def __create_dihedral_matrix(dihedrals:List[Dict[int, float]]) ->np.ndarray:
        assert all(len(dihedrals[x]) == len(dihedrals[0]) for x in range(1, len(dihedrals)))
        array = np.empty((len(dihedrals), len(dihedrals[0])),)
        for i, sub_dict in enumerate(dihedrals):
            for j, element in enumerate(sub_dict.values()):
                array[i, j] = element
        return array


    # def items(self):
    #     return zip(self.dihedrals, self.energies)
    #
    # def __len__(self):
    #     assert len(self.energies) == len(self.dihedrals)
    #     return len(self.energies)
    #
    # def get_energies(self) -> np.ndarray:
    #     return np.array(self.energies)
    #
    # def get_dihedrals(self) -> np.ndarray:
    #     shape = (len(self), sum(len(v) for k, v in self.dihedrals[0].items()))
    #     array = np.empty(shape, dtype=float)
    #     for i, dihedral_data in enumerate(self.dihedrals):
    #         j = 0
    #         for dihedral_string, dihedral_values in dihedral_data.items():
    #             k = len(dihedral_values)
    #             array[i][j:j + k] = dihedral_values
    #             j += k
    #     return array2


def read_data(data_file_path:str, mapping_file_path:str) -> DihedralDataContainer:
    reader = JsonMapFileReader(mapping_file_path)
    mapping = reader.read()
    reader = YamlEnergyReader(data_file_path)
    energy, dihedrals = reader.read()
    return DihedralDataContainer(energy, dihedrals, mapping)

if __name__ == '__main__':
    print(DihedralType('OS-CT-CT-CT', []))
    print(DihedralType('OS-CT-CT-CT', []) == DihedralType('CT-CT-CT-OS', []))
    # reader = JsonMapFileReader("/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/plik1.json")
    # mapping = reader.read()
    # reader = YamlEnergyReader("/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/E_zRB-fixed.yaml")
    # energy, dihedrals = reader.read()
    # print(dihedrals[0])
    # ddc = DihedralDataContainer(energy, dihedrals, mapping)
    ddc = read_data("/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/E_zRB-fixed.yaml", "/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/plik1.json")
    # for k, v in ddc.items():
    #     print(len(k), k)
    #     print(v)
    #     break
    # print(len(ddc))
    # print(type(ddc.get_energies()), ddc.get_energies())
    # print(ddc.get_dihedrals())
