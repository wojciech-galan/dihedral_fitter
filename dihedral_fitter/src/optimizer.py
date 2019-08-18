#! /usr/bin/python
# -*- coding: utf-8 -*-
import abc
import numpy


def rmsd(array_a: numpy.ndarray, array_b: numpy.ndarray) -> float:
    '''
    Computes root mean squared deviation between two numpy arrays. The arrays should be of the same shape
    :param array_a:
    :param array_b:
    :return:
    '''
    return numpy.sqrt(((array_a - array_b) ** 2).mean())


if __name__ == '__main__':
    # use case
    import functools
    from scipy.optimize import *

    list_1 = numpy.array(range(5))
    list_2 = list_1 * 2 + 1


    # so list_2 = a*list_1+b
    # how to find a and b?
    def equation(a, b, x1):
        return x1 * a + b


    def f_to_minimize(l1, l2, par):
        a, b = par
        return rmsd(l2, equation(a, b, l1))


    print(least_squares(functools.partial(f_to_minimize, list_1, list_2), [0, 0]).x)
    print(differential_evolution(functools.partial(f_to_minimize, list_1, list_2), [(-5, 5.1), (-50, 5)]).x)
