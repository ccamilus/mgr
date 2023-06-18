import math
import random

NUMBER_OF_SELECTED_FIELDS = 3


class MinMax:
    def __init__(self, board_size):
        self._board_size = board_size

    def _select_fields(self, cnf_result):
        max_score = cnf_result[0][0]
        fields = [result[1] for result in cnf_result if result[0] == max_score]
        if len(fields) > NUMBER_OF_SELECTED_FIELDS:
            return random.sample(fields, NUMBER_OF_SELECTED_FIELDS)
        return fields

    def _transform_index_to_coordinate(self, index):
        return ((index - 1) % self._board_size) + 1, math.ceil(index / self._board_size)

    def _transform_coordinate_to_index(self, x, y):
        return (self._board_size * y) - (self._board_size - x)

    def _get_player_score(self, game_state, computer_position_in_game_state, maximizer):
        if maximizer:
            position = computer_position_in_game_state
        else:
            position = 0 if computer_position_in_game_state == 1 else 1
        corrupted_fields = []
        for index, value in enumerate(game_state[position::2]):
            if value == 1:
                corrupted_fields.append(self._transform_index_to_coordinate(index + 1))
        if len(corrupted_fields) < 5:
            return 0
        for y in range(1, self._board_size + 1):
            fields = [corrupted_field for corrupted_field in corrupted_fields if corrupted_field[1] == y]
            if len(fields) < 5:
                continue
            else:
                for field in fields:
                    unwanted_fields = [(field[0] - 1, y), (field[0] + 5, y)]
                    if all(unwanted_field not in fields for unwanted_field in unwanted_fields):
                        wanted_fields = [(field[0] + i, y) for i in range(1, 5)]
                        if all(wanted_field in fields for wanted_field in wanted_fields):
                            return 1 if maximizer else -1
        for x in range(1, self._board_size + 1):
            fields = [field for field in corrupted_fields if field[0] == x]
            if len(fields) < 5:
                continue
            else:
                for field in fields:
                    unwanted_fields = [(x, field[1] - 1), (x, field[1] + 5)]
                    if all(unwanted_field not in fields for unwanted_field in unwanted_fields):
                        wanted_fields = [(x, field[1] + i) for i in range(1, 5)]
                        if all(wanted_field in fields for wanted_field in wanted_fields):
                            return 1 if maximizer else -1
        for field in corrupted_fields:
            unwanted_fields = [(field[0] - 1, field[1] - 1), (field[0] + 5, field[1] + 5)]
            if all(unwanted_field not in corrupted_fields for unwanted_field in unwanted_fields):
                wanted_fields = [(field[0] + i, field[1] + i) for i in range(1, 5)]
                if all(wanted_field in corrupted_fields for wanted_field in wanted_fields):
                    return 1 if maximizer else -1
        for field in corrupted_fields:
            unwanted_fields = [(field[0] + 1, field[1] - 1), (field[0] - 5, field[1] + 5)]
            if all(unwanted_field not in corrupted_fields for unwanted_field in unwanted_fields):
                wanted_fields = [(field[0] - i, field[1] + i) for i in range(1, 5)]
                if all(wanted_field in corrupted_fields for wanted_field in wanted_fields):
                    return 1 if maximizer else -1
        return 0

    def _minmax(self, minmax_game_state, depth, computer_position_in_game_state, maximizer=False):
        score = self._get_player_score(minmax_game_state, computer_position_in_game_state, not maximizer)
        if minmax_game_state.count(1) == self._board_size ** 2 or depth == 0 or score == 1 or score == -1:
            return score
        if maximizer:
            best_score = -2
            bonus = 0 + computer_position_in_game_state
            for i in range(self._board_size ** 2):
                if minmax_game_state[(i * 2)] == 0 and minmax_game_state[((i * 2) + 1)] == 0:
                    minmax_game_state[(i * 2) + bonus] = 1
                    best_score = max(best_score,
                                     self._minmax(minmax_game_state.copy(), depth - 1, computer_position_in_game_state,
                                                  False))
                    minmax_game_state[(i * 2) + bonus] = 0
            return best_score
        else:
            best_score = 2
            bonus = 1 - computer_position_in_game_state
            for i in range(self._board_size ** 2):
                if minmax_game_state[(i * 2)] == 0 and minmax_game_state[((i * 2) + 1)] == 0:
                    minmax_game_state[(i * 2) + bonus] = 1
                    best_score = min(best_score,
                                     self._minmax(minmax_game_state.copy(), depth - 1, computer_position_in_game_state,
                                                  True))
                    minmax_game_state[(i * 2) + bonus] = 0
            return best_score

    def get_best_move(self, depth, game_state, cnf_result, computer_position_in_game_state):
        selected_fields = self._select_fields(cnf_result)
        if len(selected_fields) > 1:
            fields_scores = []
            for field in selected_fields:
                minmax_game_state = game_state.copy()
                index = ((field - 1) * 2) + computer_position_in_game_state
                minmax_game_state[index] = 1
                field_score = self._minmax(minmax_game_state, depth, computer_position_in_game_state)
                fields_scores.append((field_score, field))
            max_score = max(fields_scores)[0]
            return random.choice([field[1] for field in fields_scores if field[0] == max_score])
        else:
            return selected_fields[0]
