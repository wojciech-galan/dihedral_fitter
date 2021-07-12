import json
import numpy as np
from typing import Dict
from typing import List
from typing import Iterable


def load_initial_c_params(params_f_path: str, num_of_params_per_dihedral_type: int,
                          dihedral_types: Iterable[str]) -> np.ndarray:
    with open(params_f_path) as f:
        params = json.load(f)
    validate_data_type_in_json(params)
    dihedral_types_in_file_but_not_in_proper_types = set(params) - set(dihedral_types)
    dihedral_types_in_proper_types_but_not_in_file = set(dihedral_types) - set(params)
    if dihedral_types_in_file_but_not_in_proper_types or dihedral_types_in_proper_types_but_not_in_file:
        raise RuntimeError(
            f'''Dihedral types differ between initial parameters and mapping file.
In initial parameters:  {sorted(list(params))},
In mapping:             {sorted(list(dihedral_types))}'''
        )
    validate_num_of_params_per_dihedral_type(params, num_of_params_per_dihedral_type)
    # return params in the same order as in mapping:
    ret = np.empty(num_of_params_per_dihedral_type * len(dihedral_types))
    for i, dihedral_type in enumerate(dihedral_types):
        ret[i * num_of_params_per_dihedral_type: (i + 1) * num_of_params_per_dihedral_type] = params[dihedral_type]
    return ret


def validate_data_type_in_json(params: Dict[str, List[float]]):
    if not (isinstance(params, dict) and all(isinstance(v, list) for _, v in params.items())):
        raise RuntimeError(
            '''Your file sgould look like this:
{"dihedral type 1"": [num1, num2, ..., numN],
"dihedral type 2"": [num1, num2, ..., numN],
...,
"dihedral type M"": [num1, num2, ..., numN]'''
        )


def validate_num_of_params_per_dihedral_type(params_for_dihedral_types: Dict[str, List[float]],
                                             valid_num_of_params_per_dihedral_type: int):
    for dihedral_type, params in params_for_dihedral_types.items():
        if len(params) != valid_num_of_params_per_dihedral_type:
            raise RuntimeError(f'You should provide {valid_num_of_params_per_dihedral_type} numbers for each dihedral',
                               f'type. Correct it for {dihedral_type}.')


def save_computed_params(params_array: np.ndarray, dihedral_types: Iterable[str], num_of_params_per_dihedral_type: int,
                         path: str) -> None:
    out = {}
    for i, dihedral_type in enumerate(dihedral_types):
        out[dihedral_type] = list(
            params_array[i * num_of_params_per_dihedral_type: (i + 1) * num_of_params_per_dihedral_type])
    with open(path, 'w') as f:
        json.dump(out, f, indent=4)