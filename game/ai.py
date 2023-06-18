from cnf import Cnf
from minmax import MinMax


class AI:
    def __init__(self, board_size):
        self._board_size = board_size
        self._cnf = Cnf(self._board_size)
        self._minmax = MinMax(self._board_size)

    def get_best_move(self, game_state, computer_position_in_game_state):
        cnf_result = self._cnf.get_results(game_state)
        minmax_result = self._minmax.get_best_move(2, game_state, cnf_result, computer_position_in_game_state)
        return minmax_result
