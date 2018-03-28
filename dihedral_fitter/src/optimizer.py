#! /usr/bin/python
# -*- coding: utf-8 -*-
import abc
import os
import functools
import numpy as np
from typing import Callable
from typing import List
from typing import Tuple
from scipy.optimize import least_squares
from scipy.optimize import differential_evolution
from dihedral_fitter.src.lib import ryckaert_bellemans_function
from dihedral_fitter.src.lib import rmsd_for_multiple_arrays
from dihedral_fitter.src.lib import move_to_zero
from dihedral_fitter.src.lib import substract_lists_of_arrays
from dihedral_fitter.src.reader import SimpleEnergyReader


# TODO check in the future:
# since I don't know what is the exact form of energy torsion (several possible options are:
# - energy torsion is a list of numbers (each number corresponds to a configuratio)
# - the size of energy torsion is num_of_dihedral_types x num_of_configurations
# - the size of energy torsion is num_of_dihedrals x num_of_configurations),
# I have to fake the distance measurement for the purpose of testing
def fake_rmsd(array1: List[np.ndarray], array2: List[List[float]]):
    # Let's assume that the size of energy torsion is num_of_dihedral_types x num_of_configurations
    pass


def function_to_compute_energy_torsion_wrapper(function_to_compute_energy_torsion: Callable, c_params: List[float],
                                               angles: List[float], num_of_c_params: int):
    '''
    Runs function_to_compute_energy_torsion for every dihedral type. The function is needed, because least_squares
    from scipy.optimize need one-dimensional second argument
    :param function_to_compute_energy_torsion:
    :param c_params: flatten list of coefficients for every dihedral type: for type1 then type2, then type3
    :param angles:
    :param num_of_c_params: number of coefficients for every dihedral type
    :return:
    '''
    ret_list = []
    for i in range(0, len(c_params), num_of_c_params):
        ret_list.append(function_to_compute_energy_torsion(c_params[i:i + num_of_c_params], angles))
    return ret_list


class Optimizer(abc.ABC):
    def __init__(self, function_used_for_minimization: Callable,
                 function_that_mearures_deviation: Callable = rmsd_for_multiple_arrays,
                 function_that_computes_coefficients: Callable = ryckaert_bellemans_function):
        super().__init__()
        self.function_used_for_minimization = function_used_for_minimization
        self.function_that_mearures_deviation = function_that_mearures_deviation
        self.function_that_computes_coefficients = function_that_computes_coefficients

    def minimize(self, energy_start: List[np.ndarray], energy_target: List[np.ndarray], num_of_c_params: int,
                 phi_angles: List[float], second_argument_of_function_used_for_optimization: List[float] = None,
                 num_of_dihedral_types: int = 1):
        def f_to_minimize(energy, angles, c_params):
            return self.function_that_mearures_deviation(energy, function_to_compute_energy_torsion_wrapper(
                self.function_that_computes_coefficients, c_params, angles, num_of_c_params))

        energy_diff = substract_lists_of_arrays(energy_target, energy_start)
        res = self.function_used_for_minimization(functools.partial(f_to_minimize, energy_diff, phi_angles),
                                                  second_argument_of_function_used_for_optimization)
        deviation = self.function_that_mearures_deviation(
            function_to_compute_energy_torsion_wrapper(ryckaert_bellemans_function, res.x, range(0, 360, 10), 4),
            energy_diff)
        return res.x, deviation


class LeastSquaresOptimizer(Optimizer):
    def __init__(self, function_that_mearures_deviation: Callable = rmsd_for_multiple_arrays,
                 function_that_computes_coefficients: Callable = ryckaert_bellemans_function):
        super().__init__(least_squares, function_that_mearures_deviation, function_that_computes_coefficients)

    def minimize(self, energy_start: List[np.ndarray], energy_target: List[np.ndarray], num_of_c_params: int,
                 phi_angles: List[float], initial_guess_for_c_params: List[float] = None,
                 num_of_dihedral_types: int = 1):
        if initial_guess_for_c_params is None:
            initial_guess_for_c_params = [0] * num_of_c_params * num_of_dihedral_types
        else:
            assert len(initial_guess_for_c_params) == num_of_c_params * num_of_dihedral_types

        return super().minimize(energy_start, energy_target, num_of_c_params, phi_angles, initial_guess_for_c_params,
                                num_of_dihedral_types)


class DifferentialEvolutionOptimizer(Optimizer):
    def __init__(self, function_that_mearures_deviation: Callable = rmsd_for_multiple_arrays,
                 function_that_computes_coefficients: Callable = ryckaert_bellemans_function, **params):
        print(params)
        super().__init__(functools.partial(differential_evolution, **params), function_that_mearures_deviation,
                         function_that_computes_coefficients)

    def minimize(self, energy_start: List[np.ndarray], energy_target: List[np.ndarray], num_of_c_params: int,
                 phi_angles: List[float], bounds_for_c_params: List[Tuple[float]] = None,
                 num_of_dihedral_types: int = 1):
        return super().minimize(energy_start, energy_target, num_of_c_params, phi_angles, bounds_for_c_params,
                                num_of_dihedral_types)


if __name__ == '__main__':
    import random

    lso = LeastSquaresOptimizer()
    energy_without_dihedrals = np.array(
        [move_to_zero(SimpleEnergyReader(os.path.join('sample_files', 'triacetin.mm'), 36).energies)])
    energy_qm = np.array([SimpleEnergyReader(os.path.join('sample_files', 'qm'), 36).energies])
    print(lso.minimize(energy_without_dihedrals, energy_qm, 4, list(range(0, 360, 10)),
                 [random.randint(-50, 50) for _ in range(4)], 1))
    results = {}
    for strategy in ['best1bin', 'best1exp', 'rand1exp', 'randtobest1exp', 'best2exp', 'rand2exp', 'randtobest1bin',
                     'best2bin', 'rand2bin', 'rand1bin']:
        for mutation_2 in np.linspace(1, 1.999, 3):
            for polish in (True, False):
                for init in ['latinhypercube', 'random']:
                    for recombination in np.linspace(0.1, 1, 10):
                        deo = DifferentialEvolutionOptimizer(strategy=strategy, popsize=100, mutation=(.5, mutation_2),
                                                             polish=polish, init=init, recombination=recombination,
                                                             tol=0.0001)
                        result = deo.minimize(energy_without_dihedrals, energy_qm, 4, range(0, 360, 10),
                                              [[-30, 30] for _ in range(4)], 1)
                        results[(strategy, mutation_2, polish, init, recombination)] = result
                        print(result)
    print(results.items())
    print(min(results.items(), key=lambda x: x[1][1]))

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
