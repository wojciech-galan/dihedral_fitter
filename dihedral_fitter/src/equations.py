#! /usr/bin/python
# -*- coding: utf-8 -*-

import math


def ryckaert_belleman_function(c_parameters, phi_angles):
    return sum(
        sum(math.pow(-1, n) * c_parameters[n] * math.pow(math.cos(phi), n) for n in range(len(c_parameters))) for phi in
        phi_angles)
