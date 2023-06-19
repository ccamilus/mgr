import math
import os
from pathlib import Path


class AdditionalGenerator:
    def __init__(self, board_size, time_snapshot):
        self._board_size = board_size
        self._time_snapshot = time_snapshot

    def _transform_index_to_coordinate(self, index):
        return ((index - 1) % self._board_size) + 1, math.ceil(index / self._board_size)

    def _transform_coordinate_to_index(self, x, y):
        return (self._board_size * y) - (self._board_size - x)

    def _win_checker(self, field):
        formulas = []
        number_of_clauses = 5
        formula_type = "win_checker"
        x, y = self._transform_index_to_coordinate(field)
        hx = x - 4
        for i in range(5):
            not_negated_indexes = []
            negated_indexes = []
            first_negate_x = x - 5 + i
            second_negate_x = x + 1 + i
            if 0 < first_negate_x <= self._board_size:
                negated_indexes.append((self._transform_coordinate_to_index(first_negate_x, y) - 1) * 2)
            if 0 < second_negate_x <= self._board_size:
                negated_indexes.append((self._transform_coordinate_to_index(second_negate_x, y) - 1) * 2)
            for j in range(5):
                tmp_hx = hx + i + j
                if 0 < tmp_hx <= self._board_size:
                    if tmp_hx != x:
                        not_negated_indexes.append((self._transform_coordinate_to_index(tmp_hx, y) - 1) * 2)
                else:
                    not_negated_indexes.clear()
                    negated_indexes.clear()
                    break
            if not_negated_indexes and negated_indexes:
                for negated_index in negated_indexes:
                    zero_formula = [(False, index) for index in not_negated_indexes]
                    zero_formula.append((True, negated_index))
                    one_formula = [(False, index + 1) for index in not_negated_indexes]
                    one_formula.append((True, negated_index + 1))
                    formulas.append(zero_formula)
                    formulas.append(one_formula)
        vy = y - 4
        for i in range(5):
            not_negated_indexes = []
            negated_indexes = []
            first_negate_y = y - 5 + i
            second_negate_y = y + 1 + i
            if 0 < first_negate_y <= self._board_size:
                negated_indexes.append((self._transform_coordinate_to_index(x, first_negate_y) - 1) * 2)
            if 0 < second_negate_y <= self._board_size:
                negated_indexes.append((self._transform_coordinate_to_index(x, second_negate_y) - 1) * 2)
            for j in range(5):
                tmp_vy = vy + i + j
                if 0 < tmp_vy <= self._board_size:
                    if tmp_vy != y:
                        not_negated_indexes.append((self._transform_coordinate_to_index(x, tmp_vy) - 1) * 2)
                else:
                    not_negated_indexes.clear()
                    negated_indexes.clear()
                    break
            if not_negated_indexes and negated_indexes:
                for negated_index in negated_indexes:
                    zero_formula = [(False, index) for index in not_negated_indexes]
                    zero_formula.append((True, negated_index))
                    one_formula = [(False, index + 1) for index in not_negated_indexes]
                    one_formula.append((True, negated_index + 1))
                    formulas.append(zero_formula)
                    formulas.append(one_formula)
        d1x = x - 4
        d1y = y - 4
        for i in range(5):
            not_negated_indexes = []
            negated_indexes = []
            first_negate_x = x - 5 + i
            first_negate_y = y - 5 + i
            second_negate_x = x + 1 + i
            second_negate_y = y + 1 + i
            if 0 < first_negate_x <= self._board_size and 0 < first_negate_y <= self._board_size:
                negated_indexes.append((self._transform_coordinate_to_index(first_negate_x, first_negate_y) - 1) * 2)
            if 0 < second_negate_x <= self._board_size and 0 < second_negate_y <= self._board_size:
                negated_indexes.append((self._transform_coordinate_to_index(second_negate_x, second_negate_y) - 1) * 2)
            if second_negate_x == self._board_size + 1 and first_negate_y == 0 or \
                    second_negate_y == self._board_size + 1 and first_negate_x == 0:
                negated_indexes.append((self._transform_coordinate_to_index(x, y) - 1) * 2)
            for j in range(5):
                tmp_d1x = d1x + i + j
                tmp_d1y = d1y + i + j
                if 0 < tmp_d1x <= self._board_size and 0 < tmp_d1y <= self._board_size:
                    if tmp_d1x != x and tmp_d1y != y:
                        not_negated_indexes.append((self._transform_coordinate_to_index(tmp_d1x, tmp_d1y) - 1) * 2)
                else:
                    not_negated_indexes.clear()
                    negated_indexes.clear()
                    break
            if not_negated_indexes and negated_indexes:
                for negated_index in negated_indexes:
                    zero_formula = [(False, index) for index in not_negated_indexes]
                    zero_formula.append((True, negated_index))
                    one_formula = [(False, index + 1) for index in not_negated_indexes]
                    one_formula.append((True, negated_index + 1))
                    formulas.append(zero_formula)
                    formulas.append(one_formula)
        d2x = x + 4
        d2y = y - 4
        for i in range(5):
            not_negated_indexes = []
            negated_indexes = []
            first_negate_x = x + 5 - i
            first_negate_y = y - 5 + i
            second_negate_x = x - 1 - i
            second_negate_y = y + 1 + i
            if 0 < first_negate_x <= self._board_size and 0 < first_negate_y <= self._board_size:
                negated_indexes.append(
                    (self._transform_coordinate_to_index(first_negate_x, first_negate_y) - 1) * 2)
            if 0 < second_negate_x <= self._board_size and 0 < second_negate_y <= self._board_size:
                negated_indexes.append(
                    (self._transform_coordinate_to_index(second_negate_x, second_negate_y) - 1) * 2)
            if second_negate_x == 0 and first_negate_y == 0 or \
                    second_negate_y == self._board_size + 1 and first_negate_x == self._board_size + 1:
                negated_indexes.append((self._transform_coordinate_to_index(x, y) - 1) * 2)
            for j in range(5):
                tmp_d2x = d2x - i - j
                tmp_d2y = d2y + i + j
                if 0 < tmp_d2x <= self._board_size and 0 < tmp_d2y <= self._board_size:
                    if tmp_d2x != x and tmp_d2y != y:
                        not_negated_indexes.append(
                            (self._transform_coordinate_to_index(tmp_d2x, tmp_d2y) - 1) * 2)
                else:
                    not_negated_indexes.clear()
                    negated_indexes.clear()
                    break
            if not_negated_indexes and negated_indexes:
                for negated_index in negated_indexes:
                    zero_formula = [(False, index) for index in not_negated_indexes]
                    zero_formula.append((True, negated_index))
                    one_formula = [(False, index + 1) for index in not_negated_indexes]
                    one_formula.append((True, negated_index + 1))
                    formulas.append(zero_formula)
                    formulas.append(one_formula)
        return formulas, formula_type, number_of_clauses, len(formulas)

    def _save_formulas_as_cnf_file(self, formulas, field, formula_type, number_of_clauses, number_of_formulas):
        base_path = Path(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.exists(base_path.joinpath(f"cnf/{self._time_snapshot}/additional")):
            os.makedirs(base_path.joinpath(f"cnf/{self._time_snapshot}/additional"))
        with open(base_path.joinpath(f"cnf/{self._time_snapshot}/additional/{field}_{formula_type}.cnf"), "w") as cnf:
            cnf.write(f"c {field}_{formula_type}.cnf\nc\n")
            cnf.write(f"c field = {field}\nc formula set type = {formula_type}\nc\n")
            cnf.write(f"p cnf {number_of_clauses} {number_of_formulas}\n")
            for formula in formulas:
                for literal in formula:
                    cnf.write(f"-{literal[1]} ") if literal[0] else cnf.write(f"{literal[1]} ")
                    cnf.write("\n")

    def run(self):
        field = 1
        self._win_checker(field)
        for field in range(1, (self._board_size ** 2) + 1):
            win_checker_results = self._win_checker(field)
            self._save_formulas_as_cnf_file(win_checker_results[0], field, win_checker_results[1],
                                            win_checker_results[2], win_checker_results[3])


def main():
    board_size = 15
    time_snapshot = "174223.838237"
    generator = AdditionalGenerator(board_size, time_snapshot)
    generator.run()


if __name__ == "__main__":
    main()
