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
