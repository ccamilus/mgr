import math
import os
from pathlib import Path

from cnf_util import Literal, Clause, Formula


class Field:
    def __init__(self, index, formulas):
        self.index = index
        self._formulas = formulas

    def check_formulas(self, game_state):
        logic_values = [f.get_logic_value(game_state) for f in self._formulas]
        return sum(logic_values)


class AdditionalFormulasChecker:
    def __init__(self, board_size):
        self._board_size = board_size
        self._fields = self._create_fields()

    def _create_fields(self):
        field_indexes = [index for index in range(1, self._board_size ** 2 + 1)]
        fields = []
        for fi in field_indexes:
            with open(Path(os.path.dirname(os.path.abspath(__file__))).joinpath(f"cnf/additional/{fi}_win_checker.cnf"),
                      "r") as file:
                formulas_tmp = [line.strip() for line in file if not line.startswith('c')]
                formulas = self._create_formulas(formulas_tmp[0].split()[2:5], formulas_tmp[1:])
            fields.append(Field(fi, formulas))
        return fields

    def _create_formulas(self, constants, data):
        raw_formulas = [data[i:i + int(constants[0])] for i in range(0, len(data), int(constants[0]))]
        final_formulas = []
        for formula in raw_formulas:
            final_clauses = []
            for clause in formula:
                final_literals = []
                raw_literals = clause.split()
                for literal in raw_literals:
                    if literal.startswith("-"):
                        final_literals.append(Literal(literal[1:], True))
                    else:
                        final_literals.append(Literal(literal, False))
                final_clauses.append(Clause(final_literals))
            final_formulas.append(Formula(final_clauses))
        return final_formulas

    def _transform_index_to_coordinate(self, index):
        return ((index - 1) % self._board_size) + 1, math.ceil(index / self._board_size)

    def _check_if_field_is_self_win(self, game_state, computer_position_in_game_state):
        corrupted_fields = []
        for index, value in enumerate(game_state[computer_position_in_game_state::2]):
            if value == 1:
                corrupted_fields.append(self._transform_index_to_coordinate(index + 1))
        if len(corrupted_fields) < 5:
            return False
        for y in range(1, self._board_size + 1):
            fields = [corrupted_field for corrupted_field in corrupted_fields if corrupted_field[1] == y]
            if len(fields) < 5:
                continue
            else:
                for field in fields:
                    unwanted_fields = [(field[0] - 1, y), (field[0] + 5, y)]
                    if all(unwanted_field not in fields for unwanted_field in unwanted_fields):
                        wanted_fields = [(field[0] + i, y) for i in range(1, 5)]
                        return all(wanted_field in fields for wanted_field in wanted_fields)
        for x in range(1, self._board_size + 1):
            fields = [field for field in corrupted_fields if field[0] == x]
            if len(fields) < 5:
                continue
            else:
                for field in fields:
                    unwanted_fields = [(x, field[1] - 1), (x, field[1] + 5)]
                    if all(unwanted_field not in fields for unwanted_field in unwanted_fields):
                        wanted_fields = [(x, field[1] + i) for i in range(1, 5)]
                        return all(wanted_field in fields for wanted_field in wanted_fields)
        for field in corrupted_fields:
            unwanted_fields = [(field[0] - 1, field[1] - 1), (field[0] + 5, field[1] + 5)]
            if all(unwanted_field not in corrupted_fields for unwanted_field in unwanted_fields):
                wanted_fields = [(field[0] + i, field[1] + i) for i in range(1, 5)]
                return all(wanted_field in corrupted_fields for wanted_field in wanted_fields)
        for field in corrupted_fields:
            unwanted_fields = [(field[0] + 1, field[1] - 1), (field[0] - 5, field[1] + 5)]
            if all(unwanted_field not in corrupted_fields for unwanted_field in unwanted_fields):
                wanted_fields = [(field[0] - i, field[1] + i) for i in range(1, 5)]
                return all(wanted_field in corrupted_fields for wanted_field in wanted_fields)
        return False

    def check_formulas(self, game_state, computer_position_in_game_state):
        corrupted_fields = []
        for index, value in enumerate(game_state):
            if value == 1:
                if index % 2 == 0:
                    corrupted_fields.append((index // 2) + 1)
                else:
                    corrupted_fields.append(((index - 1) // 2) + 1)
        results = []
        for field in self._fields:
            if field.index not in corrupted_fields:
                result = field.check_formulas(game_state)
                if result > 0:
                    results.append(field.index)
        results.sort(reverse=True)
        for result in results:
            result_game_state = game_state.copy()
            result_game_state[((result - 1) * 2) + computer_position_in_game_state] = 1
            if self._check_if_field_is_self_win(result_game_state, computer_position_in_game_state):
                return [result]
        return results
