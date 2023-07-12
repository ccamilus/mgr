import math
import os
from pathlib import Path


def transform_index_to_coordinate(index, board_size):
    return ((index - 1) % board_size) + 1, math.ceil(index / board_size)


def transform_coordinate_to_index(x, y, board_size):
    return (board_size * y) - (board_size - x)


def save_formulas_as_cnf_file(formulas, field, output_path, formula_type, number_of_clauses, number_of_formulas):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with open(Path(output_path).joinpath(f"{field}_{formula_type}.cnf"), "w") as cnf_file:
        cnf_file.write(f"c {field}_{formula_type}.cnf\nc\n")
        cnf_file.write(f"c field = {field}\nc formula set type = {formula_type}\nc\n")
        cnf_file.write(f"p cnf {number_of_clauses} {number_of_formulas}\n")
        for formula in formulas:
            for clause in formula:
                for literal in clause:
                    cnf_file.write(f"-{literal[1]} ") if literal[0] else cnf_file.write(f"{literal[1]} ")
                cnf_file.write("\n")
