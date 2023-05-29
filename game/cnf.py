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
        result = sum(one_logic_values) - sum(zero_logic_values)
        return result, self._index


class Cnf:
    def __init__(self, board_size):
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
            with open(Path(os.path.dirname(os.path.abspath(__file__))).joinpath(f"formulas/{fi}-neg.cnf"), "r") as file:
                zeros_tmp = [line.strip() for line in file if not line.startswith('c')]
                zeros = self._create_formulas(zeros_tmp[0].split()[2:5], zeros_tmp[1:])
            with open(Path(os.path.dirname(os.path.abspath(__file__))).joinpath(f"formulas/{fi}-pos.cnf"), "r") as file:
                ones_tmp = [line.strip() for line in file if not line.startswith('c')]
                ones = self._create_formulas(ones_tmp[0].split()[2:5], ones_tmp[1:])
            fields.append(Field(fi, ones, zeros))
        return fields

    def _create_formulas(self, constants, data):
        raw_formulas = [data[i:i + int(constants[1])] for i in range(0, len(data), int(constants[1]))]
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

    def get_result(self, game_state):
        result = []
        for field in self._fields:
            result.append(field.check_formulas(game_state))
        return result
