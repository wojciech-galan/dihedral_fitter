#! /usr/bin/python
# -*- coding: utf-8 -*-

import math
from typing import Sequence
from typing import Union
from typing import Iterable


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
