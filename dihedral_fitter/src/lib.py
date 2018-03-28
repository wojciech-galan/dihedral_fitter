#! /usr/bin/python
# -*- coding: utf-8 -*-

import math
import numpy as np
from typing import Sequence
from typing import Union
from typing import Iterable
from typing import List


def ryckaert_bellemans_function(c_parameters: Sequence[Union[int, float]],
                                phi_angles: Iterable[Union[int, float]]) -> List[float]:
    """
    Computes Ryckaert-Bellmans function for given C parameters and phi angles  for one type of dihedrals using
    the formula:
    f(phi) = sum_n_from_0_to_len_c_params( (-1)^n*Cn*cos^n(phi)) )
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
    return np.sqrt(((array_a - array_b) ** 2).mean())


def move_to_zero(num_list: List[List[float]]) -> List[List[float]]:
    """
    Transforms input values to be >= 0 by subtracting minimal value
    :param num_list:
    :return:
    """
    minimum = min([y for sub_list in num_list for y in sub_list])
    return [[y - minimum for y in sub_list] for sub_list in num_list]


def rmsd_for_multiple_arrays(data_a: List[np.ndarray], data_b: List[np.ndarray]) -> float:
    """
    Computes root mean square deviation between lists of numpy arrays
    """
    assert len(data_a) == len(data_b)
    if len(data_a) == 1:
        return rmsd(data_a[0], data_b[0])
    else:
        # all of the arrays in data_a should have the same second dimension
        second_dimension = data_a[0].shape[1]
        assert all([array.shape[1] == second_dimension for array in data_a])
        accumulator = []
        for i in range(len(data_a)):
            accumulator.extend(((data_a[i] - data_b[i]) ** 2).flatten())
        return np.sqrt(np.mean(accumulator))


def substract_lists_of_arrays(data_a: List[np.ndarray], data_b: List[np.ndarray]) -> List[np.ndarray]:
    """
    Takes two lists of arrays and computes the difference.
    The lists must be of the same length and corresponding elements must have the same shape.
    """
    assert len(data_a) == len(data_b)
    assert all(data_a[i].shape==data_b[i].shape for i in range(len(data_a)))
    ret_list = []
    for i in range(len(data_a)):
        # print(data_a[i])
        # print(data_b[i])
        ret_list.append(data_a[i] - data_b[i])
    return ret_list
