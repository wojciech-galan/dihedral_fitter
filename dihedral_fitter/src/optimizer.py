#! /usr/bin/python
# -*- coding: utf-8 -*-
import abc
import sys
import functools
import math
import numpy as np
from typing import Callable
from typing import List
from typing import Dict
from typing import Tuple
from scipy.optimize import least_squares
from scipy.optimize import differential_evolution
from dihedral_fitter.src.lib import ryckaert_bellemans_function
from dihedral_fitter.src.lib import rmsd_for_multiple_arrays
from dihedral_fitter.src.lib import rmsd
from dihedral_fitter.src.lib import rev_dict
from dihedral_fitter.src.lib import move_to_zero
from dihedral_fitter.src.lib import substract_lists_of_arrays
from dihedral_fitter.src.reader import read_data

np.set_printoptions(threshold=sys.maxsize)


# TODO check in the future:
# since I don't know what is the exact form of energy torsion (several possible options are:
# - energy torsion is a list of numbers (each number corresponds to a configuratio)
# - the size of energy torsion is num_of_dihedral_types x num_of_configurations
# - the size of energy torsion is num_of_dihedrals x num_of_configurations),
# I have to fake the distance measurement for the purpose of testing
def fake_rmsd(array1: List[np.ndarray], array2: List[List[float]]):
    # Let's assume that the size of energy torsion is num_of_dihedral_types x num_of_configurations
    pass


# Todo proper tests for rmsd and rmsd_for_multiple_arrays. Now rmsd works as expected due to second array broadcasting


def function_to_compute_energy_torsion_wrapper(function_to_compute_energy_torsion: Callable, c_params: List[float],
                                               angles: List[float], num_of_c_params: int, mapping_phi_array_index_to_dihedral_type_number:Dict[int, int]):
    '''
    Runs function_to_compute_energy_torsion for every dihedral type. The function is needed, because least_squares
    from scipy.optimize need one-dimensional second argument
    :param function_to_compute_energy_torsion:
    :param c_params: flatten list of coefficients for every dihedral type: for type1 then type2, then type3
    :param angles:
    :param num_of_c_params: number of coefficients for every dihedral type
    :return:
    '''
    #function_to_compute_energy_torsion(c_params, angle)
    ## angles - np.array (1836, 51)
    ret_arr = np.zeros(angles.shape[0])
    # for dihedral_type_number, phi_array_indices in mapping_dihedral_type_number_to_phi_array_indices.items():
    #     for phi_array_index in phi_array_indices:
    #         print(dihedral_type_number, phi_array_index)
    #         angle_set = angles[phi_array_index]
    #         c_params_for_this_dihedlal_type = c_params[dihedral_type_number*num_of_c_params: (dihedral_type_number+1)*num_of_c_params]
    #         ret_arr[phi_array_index] = sum(function_to_compute_energy_torsion(c_params_for_this_dihedlal_type, angle) for angle in angle_set)źle! talica energii ma byc dłuższa!
    for i, angle_set in enumerate(angles):
        #for dihedral_type_number, phi_array_indices in mapping_dihedral_type_number_to_phi_array_indices.values():
        #żeby policzyć energie trzeba dodac cały angle set, natomiast parametry muszą byc rane ograniczone
        #ret_arr[i] = sum(function_to_compute_energy_torsion(c_params[j*num_of_c_params:(j+1) * num_of_c_params], angle) for j, angle in enumerate(angle_set))
        for j, angle in enumerate(angle_set):
            dihedral_type_number = mapping_phi_array_index_to_dihedral_type_number[j]
            c_params_for_this_dihedlal_type = c_params[dihedral_type_number * num_of_c_params: (dihedral_type_number + 1) * num_of_c_params]
            ret_arr[i] += function_to_compute_energy_torsion(c_params_for_this_dihedlal_type, angle)
    return ret_arr


class Optimizer(abc.ABC):
    def __init__(self, function_used_for_minimization: Callable,
                 function_that_mearures_deviation: Callable = rmsd,
                 function_that_computes_coefficients: Callable = ryckaert_bellemans_function):
        super().__init__()
        self.function_used_for_minimization = function_used_for_minimization
        self.function_that_mearures_deviation = function_that_mearures_deviation
        self.function_that_computes_coefficients = function_that_computes_coefficients

    def minimize(self, energy_start: float, energy_target: float, num_of_c_params: int,
                 phi_angles: np.ndarray, mapping_between_dihedral_type_and_phi_angles_array_index:Dict[str, List[int]], second_argument_of_function_used_for_optimization: List[float] = None):
        def f_to_minimize(energy, c_params):
            mapping_phi_array_index_to_dihedral_type_number = {sub_val:i for i, v in enumerate(mapping_between_dihedral_type_and_phi_angles_array_index.values()) for sub_val in v}
            #print(mapping_dihedral_type_number_to_phi_array_indices)
            computed_energy = function_to_compute_energy_torsion_wrapper(
                self.function_that_computes_coefficients, c_params, phi_angles, num_of_c_params, mapping_phi_array_index_to_dihedral_type_number)
            print(c_params)
            #print(np.round(computed_energy))
            deviation = self.function_that_mearures_deviation(energy, computed_energy)
            print("RMSD = ", deviation, "required energy = ", energy[0])
            return deviation

        energy_diff = [energy_target - energy_start] * phi_angles.shape[0]
        # print(phi_angles.shape)
        # raise
        # print(type(second_argument_of_function_used_for_optimization))
        # print(len(second_argument_of_function_used_for_optimization))
        # print(len(second_argument_of_function_used_for_optimization[0]))
        # raise
        print(second_argument_of_function_used_for_optimization.shape)
        res = self.function_used_for_minimization(functools.partial(f_to_minimize, energy_diff), #least squares(rmsd
                                                  # <w środku wrapper(self.function_that_computes_coefficients, c_params, angles, num_of_c_params)>,  phi_angles.shape
                                                  second_argument_of_function_used_for_optimization)#, diff_step=0.1) #initial guess for c params (204 floaty)
        print('res =', res)
        print(len(res))
        import pdb
        pdb.set_trace()
        # 1. rmsd powinno przyjmować i zwracać dane o takim samym kształcie (204 w tym przypadku)
        # wrapper powinien zwracać dane dla rmsd, więc listę / tablicę 204 liczb
        deviation = self.function_that_mearures_deviation(
            function_to_compute_energy_torsion_wrapper(self.function_that_computes_coefficients, res.x,
                                                       [x * math.pi / 180 for x in range(0, 360, 10)], 4), energy_diff)
        print(deviation)
        return res.x, deviation


class LeastSquaresOptimizer(Optimizer):
    def __init__(self, function_that_mearures_deviation: Callable = rmsd,
                 function_that_computes_coefficients: Callable = ryckaert_bellemans_function):
        super().__init__(least_squares, function_that_mearures_deviation, function_that_computes_coefficients)

    def minimize(self, energy_start: List[np.ndarray], energy_target: List[np.ndarray], num_of_c_params: int,
                 phi_angles: np.ndarray, mapping_between_dihedral_type_and_phi_angles_array_index:Dict[str, List[int]], initial_guess_for_c_params: List[float] = None):
        if initial_guess_for_c_params is None:
            initial_guess_for_c_params = [0] * num_of_c_params * num_of_dihedral_types
        # else:
        #     assert len(initial_guess_for_c_params) == num_of_c_params * num_of_dihedral_types

        return super().minimize(energy_start, energy_target, num_of_c_params, phi_angles, mapping_between_dihedral_type_and_phi_angles_array_index, initial_guess_for_c_params)


class DifferentialEvolutionOptimizer(Optimizer):
    def __init__(self, function_that_mearures_deviation: Callable = rmsd,
                 function_that_computes_coefficients: Callable = ryckaert_bellemans_function, **params):
        print(params)
        super().__init__(functools.partial(differential_evolution, **params), function_that_mearures_deviation,
                         function_that_computes_coefficients)

    def minimize(self, energy_start: List[np.ndarray], energy_target: List[np.ndarray], num_of_c_params: int,
                 phi_angles: np.ndarray, mapping_between_dihedral_type_and_phi_angles_array_index:Dict[str, List[int]], bounds_for_c_params: List[Tuple[float]] = None):
        return super().minimize(energy_start, energy_target, num_of_c_params, phi_angles, mapping_between_dihedral_type_and_phi_angles_array_index, bounds_for_c_params)


if __name__ == '__main__':
    import random
    data_qm = read_data("/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/E_qm-fixed.yaml", "/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/plik1.json")
    data_without_dihedrals = read_data("/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/E_zRB-fixed.yaml", "/home/wojtek/PycharmProjects/dihedral_fitter/sample_files/plik1.json")
    mapping = data_qm.dihedral_type_to_row_index_mapping
    assert data_without_dihedrals.dihedral_type_to_row_index_mapping == mapping
    print(mapping)
    raise

    lso = LeastSquaresOptimizer()
    # energy_without_dihedrals = data_without_dihedrals.energy
    # energy_qm = [np.array(SimpleEnergyReader(os.path.join('sample_files', 'qm'), 36).energies)]
    assert np.array_equal(data_qm.dihedrals,  data_without_dihedrals.dihedrals)
    num_of_coefficients = 4
    #initial_c_coefficients = np.random.randint(-5, 5, len(mapping)*num_of_coefficients)
#     res = active_mask: array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#                               0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#                               0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
#     cost: 0.13332265558938425
#     fun: array([0.5163771])
# grad: array([-0.01093212, 0.02155936, 0.00034781, -0.03821792, -0.02186419,
#              0.01468101, -0.00839014, -0.02921202, -0.00546601, -0.00080096,
#              0.00327004, -0.00592033, -0.01093209, -0.00803873, 0.01363186,
#              0.00343549, -0.01639838, 0.03410546, -0.01642257, -0.02440134,
#              -0.04919226, -0.01728795, -0.02460324, 0.02360387, -0.02186395,
#              -0.02377248, -0.00609584, 0.0242148, -0.02733101, -0.00749166,
#              -0.0146786, 0.01334343, -0.03279742, 0.00981386, -0.02135695,
#              -0.0060705, -0.04919287, 0.00027789, -0.02680976, -0.00974653,
#              -0.01093192, -0.01731815, -0.01176429, 0.02700598, -0.02186359,
#              0.03250238, -0.00834801, -0.03500996])
# jac: array([[-0.02117081, 0.04175118, 0.00067355, -0.07401164, -0.04234152,
#              0.0284308, -0.01624809, -0.0565711, -0.0105853, -0.00155112,
#              0.00633267, -0.01146513, -0.02117076, -0.01556756, 0.02639905,
#              0.00665306, -0.03175661, 0.06604759, -0.03180344, -0.04725489,
#              -0.09526422, -0.03347931, -0.04764587, 0.04571053, -0.04234105,
#              -0.04603706, -0.01180501, 0.04689363, -0.05292838, -0.01450811,
#              -0.02842612, 0.02584048, -0.06351448, 0.01900522, -0.04135921,
#              -0.01175594, -0.09526539, 0.00053816, -0.05191896, -0.01887482,
#              -0.02117041, -0.0335378, -0.02278237, 0.05229895, -0.04234035,
#              0.0629431, -0.0161665, -0.0677992]])
# message: 'The maximum number of function evaluations is exceeded.'
# nfev: 4800
# njev: 4745
# optimality: 0.0491928666691743
# status: 0
# success: False
# x: array([-2.96689036, 0.94010348, 0.12473224, -1.21876467, -0.9337825,
#           0.3552738, 0.04355902, -0.48686368, 1.01655316, 0.38365019,
#           0.22422024, -0.33107577, -1.96689125, -0.11548417, 0.23846179,
#           0.1673942, -4.95032944, 0.94624218, -0.19143961, -1.07496177,
#           3.14892331, -0.37946141, 0.0245532, 0.42592627, 1.06620997,
#           -0.34767492, 0.10859829, 0.41728414, -4.91720465, -0.19237348,
#           -0.02500108, 0.30327635, -4.900639, 0.06053931, -0.11893078,
#           -0.03375713, 2.14894173, 0.04694713, -0.03287068, -0.10714905,
#           4.03310329, -0.46278734, -0.03677565, 0.69004432, 4.0661991,
#           0.51454562, 0.03186367, -0.67399271])
    initial_c_coefficients = np.array([-2.96393948, -0.0879202286,3, -4,-0.927879302, -0.0306774712, -3, -4, 1.01802998, -0.81574238, 0, -2, -1.96393962, -0.608602419, 4, 0, -4.94590823, -0.416282355,
                                       1, -4, 3.16226096, 0.337666635, 0,4, 1.07211954, -0.0022174847, -1, 3, -4.90984527, 0.0207128695, -4, 0, -4.89181326, 0.041204194, -3, -1, 2.16226395, 0.190817333,
                                        4, 0, 4.03605951, -0.107130887, -4, 3, 4.07211778, 0.0458433895, 3, -4])
    print(lso.minimize(data_without_dihedrals.energy, data_qm.energy, num_of_coefficients, data_qm.dihedrals, mapping,
                       initial_c_coefficients))
    raise
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
                        result = deo.minimize(energy_without_dihedrals, energy_qm, 4,
                                              angle_range, [[-30, 30] for _ in range(4)], 1)
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
    # [8.69132761e-02  7.90876809e-01  9.92873194e-01  2.08032854e+00
    #  - 2.98271981e+00  4.12489927e-02  1.65548130e+00  1.75244261e+00
    #  1.86913276e-01  8.93461602e-01 - 2.31967674e+00  7.76703400e-01
    #  8.69132761e-02  1.75319585e+00  9.92873194e-01  3.89276582e-01
    #  8.69132761e-02  4.25428800e-01 - 9.02238502e-02  1.73262164e+00
    #  8.69132761e-02  1.41969609e+00  2.31823541e+00  1.45040102e+00
    #  1.65548130e+00  2.29628749e+00  8.69132761e-02  4.15757929e+00
    #  - 9.94335729e-01  3.43688650e+00  8.69132761e-02  1.64514349e+00
    #  - 9.94335729e-01  2.55905555e+00  1.65548130e+00  3.70159195e+00
    #  - 1.65692353e+00  4.17133343e+00  2.31823541e+00  3.70015795e+00
    #  - 1.65692353e+00  4.03178084e+00 - 9.94335729e-01  1.55071896e-01
    #  - 9.02238502e-02 - 1.01132843e-01 - 1.65692353e+00  1.31200642e+00
    #  - 2.31967674e+00  1.16886153e+00  1.65548130e+00 - 5.24650073e-01
    #  9.92873194e-01  1.13854537e+00 - 2.98271981e+00 - 5.05433512e-01
    #  - 9.94335729e-01  5.35365839e-03 - 9.94335729e-01 - 1.45280198e-01
    #  - 2.98271981e+00  5.20923899e-01 - 9.94335729e-01 - 5.44901995e-01
    #  - 9.02238502e-02  1.58312163e+00 - 9.02238502e-02  2.50126113e-01
    #  9.92873194e-01  2.53180278e+00  8.69132761e-02 - 8.59641857e-05
    #  - 9.02238502e-02  1.89671444e+00 - 1.65692353e+00  2.96994503e+00
    #  - 9.02238502e-02  1.20793736e+00  2.98130801e+00  1.22122675e+00
    #  9.92873194e-01  4.07878970e-01  2.31823541e+00  2.05728001e+00
    #  - 2.98271981e+00  1.90601021e+00 - 2.98271981e+00  2.68368941e+00
    #  - 2.98271981e+00  2.09797752e+00  8.69132761e-02  1.27272976e-01
    #  - 9.02238502e-02  1.46654097e+00  1.65548130e+00  7.31842777e-02
    #  2.98130801e+00  8.80953223e-01  1.65548130e+00  2.16199878e+00
    #  1.65548130e+00  6.19436714e-01]
