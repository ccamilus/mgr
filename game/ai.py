import random

from additional_formulas import AdditionalFormulasChecker
from main_formulas import MainFormulasChecker
from minmax import MinMax


class AI:
    def __init__(self, board_size):
        self._board_size = board_size
        self._main_formulas_checker = MainFormulasChecker(self._board_size)
        self._additional_formulas_checker = AdditionalFormulasChecker(self._board_size)
        self._minmax = MinMax(self._board_size)

    def get_best_move(self, game_state, computer_position_in_game_state):
        additional_formulas_checker_result = \
            self._additional_formulas_checker.check_formulas(game_state, computer_position_in_game_state)
        if additional_formulas_checker_result:
            return random.choice(additional_formulas_checker_result)
        main_formulas_checker_result = self._main_formulas_checker.check_formulas(game_state)
        minmax_result = self._minmax.get_best_move(2, game_state, main_formulas_checker_result,
                                                   computer_position_in_game_state)
        return minmax_result
