import random

from cnf import Cnf


class AI:
    def __init__(self, board_size):
        self._cnf = Cnf(15)
        self._board_size = board_size

    def get_best_move(self, game_state):
        cnf_results = self._cnf.get_results(game_state)

        # TEMPORARY MOCKING
        return random.randint(1, 225)
