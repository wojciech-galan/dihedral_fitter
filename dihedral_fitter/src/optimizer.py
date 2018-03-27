#! /usr/bin/python
# -*- coding: utf-8 -*-
import abc
import os
import functools
import numpy as np
from typing import Callable
from typing import List
from scipy.optimize import least_squares
from scipy.optimize import differential_evolution
from dihedral_fitter.src.equations import ryckaert_bellemans_function
from dihedral_fitter.src.reader import SimpleEnergyReader


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


class Optimizer(abc.ABC):
    def __init__(self, function_used_for_minimization: Callable, function_that_mearures_deviation: Callable = rmsd):
        super().__init__()
        self.function_used_for_minimization = function_used_for_minimization
        self.function_that_mearures_deviation = function_that_mearures_deviation


class LeastSquaresOptimizer(Optimizer):
    def __init__(self, function_that_mearures_deviation: Callable = rmsd):
        super().__init__(least_squares, function_that_mearures_deviation)

    def minimize(self, energy_start: np.ndarray, energy_target: np.ndarray, num_of_c_params: int, phi_angles,
                 initial_guess_for_c_params: List[float] = None):
        if initial_guess_for_c_params is None:
            initial_guess_for_c_params = [0] * num_of_c_params
        else:
            assert len(initial_guess_for_c_params) == num_of_c_params

        def f_to_minimize(energy_torsion, angles, c_params):
            return self.function_that_mearures_deviation(energy_torsion, ryckaert_bellemans_function(c_params, angles))
        # print(energy_target.energies)
        # print(energy_start.energies)
        energy_diff = np.array(energy_target.energies) - np.array(energy_start.energies)
        # print(energy_diff)
        res = self.function_used_for_minimization(functools.partial(f_to_minimize, energy_diff, phi_angles),
                                                  initial_guess_for_c_params).x
        print(res)
        print(np.array(energy_target.energies))
        print(ryckaert_bellemans_function(res, range(0, 360, 10)))


class DifferentialEvolutionOptimizer(Optimizer):
    def __init__(self, function_that_mearures_deviation: Callable = rmsd):
        super().__init__(differential_evolution, function_that_mearures_deviation)


def minimize(function_to_be_minimized: Callable, function_that_mearures_deviation: Callable, energy_start: np.ndarray,
             energy_target: np.ndarray, c_parameters, phi_angles): pass


if __name__ == '__main__':
    import random
    lso = LeastSquaresOptimizer()
    energy_without_dihedrals = SimpleEnergyReader(os.path.join('sample_files', 'triacetin.mm'), 36)
    energy_qm = SimpleEnergyReader(os.path.join('sample_files', 'qm'), 36)
    lso.minimize(energy_without_dihedrals, energy_qm, 4, list(range(0, 360, 10)), [random.randint(-50, 50) for _ in range(4)])

    # use case
    # import functools
    # from scipy.optimize import *
    #
    # list_1 = np.array(range(5))
    # list_2 = list_1 * 2 + 1
    #
    #
    # # so list_2 = a*list_1+b
    # # how to find a and b?
    # def equation(a, b, x1):
    #     return x1 * a + b
    #
    #
    # def f_to_minimize(l1, l2, par):
    #     a, b = par
    #     return rmsd(l2, equation(a, b, l1))
    #
    #
    # print(least_squares(functools.partial(f_to_minimize, list_1, list_2), [0, 0]).x)
    # print(differential_evolution(functools.partial(f_to_minimize, list_1, list_2), [(-5, 5.1), (-50, 5)]).x)
