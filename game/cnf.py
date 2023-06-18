import math
import os
from pathlib import Path


class Literal:
    def __init__(self, index, negate):
        self.index = index
        self.negate = negate

    def get_logic_value(self, game_state):
        return not bool(game_state[int(self.index)]) if self.negate else bool(game_state[int(self.index)])


class Clause:
    def __init__(self, literals):
        self._literals = literals

    def get_logic_value(self, game_state):
        literals_logic_values = [literal.get_logic_value(game_state) for literal in self._literals]
        return any(literals_logic_values)


class Formula:
    def __init__(self, clauses):
        self._clauses = clauses

    def get_logic_value(self, game_state):
        clauses_logic_values = [clause.get_logic_value(game_state) for clause in self._clauses]
        return all(clauses_logic_values)


class Field:
    def __init__(self, index, formulas_for_ones, formulas_for_zeros):
        self._index = index
        self._formulas_for_ones = formulas_for_ones
        self._formulas_for_zeros = formulas_for_zeros

    def check_formulas(self, game_state):
        one_logic_values = [f.get_logic_value(game_state) for f in self._formulas_for_ones]
        zero_logic_values = [f.get_logic_value(game_state) for f in self._formulas_for_zeros]
        return sum(one_logic_values) - sum(zero_logic_values), self._index


class Cnf:
    def __init__(self, board_size):
        self._board_size = board_size
        self._fields = self._create_fields(board_size)

    def _create_fields(self, board_size):
        field_indexes = []
        oddity_bonus = 0 if board_size % 2 == 0 else 1
        center = (board_size // 2) + oddity_bonus
        for i in range(1, center + 1):
            for j in range(1, i + 1):
                field_indexes.append((board_size * i) - (board_size - j))
        fields = []
        for fi in field_indexes:
            with open(Path(os.path.dirname(os.path.abspath(__file__))).joinpath(f"cnf/{fi}_0.cnf"), "r") as file:
                zeros_tmp = [line.strip() for line in file if not line.startswith('c')]
                zeros = self._create_formulas(zeros_tmp[0].split()[2:5], zeros_tmp[1:])
            with open(Path(os.path.dirname(os.path.abspath(__file__))).joinpath(f"cnf/{fi}_1.cnf"), "r") as file:
                ones_tmp = [line.strip() for line in file if not line.startswith('c')]
                ones = self._create_formulas(ones_tmp[0].split()[2:5], ones_tmp[1:])
            fields.append(Field(fi, ones, zeros))
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

    def _transform_coordinate_to_index(self, x, y):
        return (self._board_size * y) - (self._board_size - x)

    def _perform_symmetry_on_field(self, index, classifier):
        x, y = self._transform_index_to_coordinate(index)
        match classifier:
            case "t":
                return index
            case "v":
                return self._transform_coordinate_to_index(self._board_size - x + 1, y)
            case "h":
                return self._transform_coordinate_to_index(x, self._board_size - y + 1)
            case "d1":
                return self._transform_coordinate_to_index(y, x)
            case "d2":
                return self._transform_coordinate_to_index(self._board_size - y + 1, self._board_size - x + 1)

    def _perform_symmetry_on_game_state(self, game_state, classifier):
        game_state_after_symmetry = [0 for _ in range((self._board_size ** 2) * 2)]
        for i in range(len(game_state)):
            if game_state[i] == 1:
                player = 0
                if not (i % 2 == 0):
                    i -= 1
                    player += 1
                index = (i // 2) + 1
                index_after_symmetry = self._perform_symmetry_on_field(index, classifier)
                new_array_index = ((index_after_symmetry - 1) * 2) + player
                game_state_after_symmetry[new_array_index] = 1
        return game_state_after_symmetry

    def get_results(self, game_state):
        corrupted_fields = []
        for index, value in enumerate(game_state):
            if value == 1:
                if index % 2 == 0:
                    corrupted_fields.append((index // 2) + 1)
                else:
                    corrupted_fields.append(((index - 1) // 2) + 1)
        results_dictionary = {}
        symmetry_groups = [["t"], ["v"], ["h"], ["d1"], ["d2"], ["v", "d1"], ["h", "v"], ["h", "d1"]]
        for group in symmetry_groups:
            game_state_after_symmetry = game_state.copy()
            for classifier in group:
                game_state_after_symmetry = self._perform_symmetry_on_game_state(game_state_after_symmetry, classifier)
            for field in self._fields:
                result = field.check_formulas(game_state_after_symmetry)
                index = result[1]
                for classifier in group:
                    index = self._perform_symmetry_on_field(index, classifier)
                if index not in results_dictionary:
                    results_dictionary[index] = result[0]
                else:
                    if result[0] > results_dictionary[index]:
                        results_dictionary[index] = result[0]
        for field in corrupted_fields:
            del results_dictionary[field]
        results = [(value, key) for key, value in results_dictionary.items()]
        results.sort(reverse=True)
        return results
