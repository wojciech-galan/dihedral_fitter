#! /usr/bin/python
# -*- coding: utf-8 -*-

import math
import numpy as np
from typing import Sequence
from typing import Union
from typing import Iterable
from typing import List


# def ryckaert_bellemans_function(c_parameters: Sequence[Union[int, float]],
#                                 phi_angles: Iterable[Union[int, float]]) -> float:
#     """
#     Computes Ryckaert-Bellmans function for given C parameters and phi angles using the formula:
#     sum_phi(  sum_n_from_0_to_len_c_params( (-1)^n*Cn*cos^n(phi)) ) )
#     """
#     return sum(
#         sum(math.pow(-1, n) * c_parameters[n] * math.pow(math.cos(phi), n) for n in range(len(c_parameters))) for phi in
#         phi_angles)

def ryckaert_bellemans_function(c_parameters: Sequence[Union[int, float]],
                                phi_angles: Iterable[Union[int, float]]) -> float:
    """
    Computes Ryckaert-Bellmans function for given C parameters and phi angles using the formula:
    sum_phi(  sum_n_from_0_to_len_c_params( (-1)^n*Cn*cos^n(phi)) ) )
    """
    return [
        sum(math.pow(-1, n) * c_parameters[n] * math.pow(math.cos(phi), n) for n in range(len(c_parameters))) for phi in
        phi_angles]


def rmsd(array_a: np.ndarray, array_b: np.ndarray) -> float:
    '''
    Computes root mean squared deviation between two numpy arrays. The arrays should be of the same shape
    :param array_a:
    :param array_b:
    :return:
    '''
    # print(array_a)
    # print(array_b)
    print(np.sqrt(((array_a - array_b) ** 2).mean()))
    return np.sqrt(((array_a - array_b) ** 2).mean())


def move_to_zero(num_list: List[List[float]]) -> List[List[float]]:
    """
    Transforms input values to be >= 0 by subtracting minimal value
    :param num_list:
    :return:
    """
    minimum = min([y for sub_list in num_list for y in sub_list])
    return [[y - minimum for y in sub_list] for sub_list in num_list]
