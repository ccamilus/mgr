import math


class AI:
    def __init__(self, cnf, board_size):
        self._cnf = cnf
        self._board_size = board_size

    def get_best_move(self, game_state):
        decision = None
        cnf_result = self._get_cnf_result(game_state)
        cnf_result.sort(reverse=True)
        while len(cnf_result) > 0:
            move = max(cnf_result)
            if game_state[move[1] * 2] == 1 or game_state[(move[1] * 2) + 1] == 1:
                cnf_result.remove(move)
            else:
                decision = move[1]
                break
        return decision

    def _get_cnf_result(self, game_state):
        cnf_result = self._cnf.get_result(game_state)
        tmp_game_state = self._perform_symmetry_on_game_state(game_state, "d1")
        tmp_result = self._cnf.get_result(tmp_game_state)
        cnf_result += self._perform_symmetry_on_cnf_result(tmp_result, "d1")
        tmp_game_state = self._perform_symmetry_on_game_state(
            self._perform_symmetry_on_game_state(game_state, "v"), "d1")
        tmp_result = self._cnf.get_result(tmp_game_state)
        cnf_result += self._perform_symmetry_on_cnf_result(self._perform_symmetry_on_cnf_result(tmp_result, "v"), "d1")
        tmp_game_state = self._perform_symmetry_on_game_state(game_state, "v")
        tmp_result = self._cnf.get_result(tmp_game_state)
        cnf_result += self._perform_symmetry_on_cnf_result(tmp_result, "v")
        tmp_game_state = self._perform_symmetry_on_game_state(game_state, "h")
        tmp_result = self._cnf.get_result(tmp_game_state)
        cnf_result += self._perform_symmetry_on_cnf_result(tmp_result, "h")
        tmp_game_state = self._perform_symmetry_on_game_state(
            self._perform_symmetry_on_game_state(game_state, "h"), "d1")
        tmp_result = self._cnf.get_result(tmp_game_state)
        cnf_result += self._perform_symmetry_on_cnf_result(self._perform_symmetry_on_cnf_result(tmp_result, "h"), "d1")
        tmp_game_state = self._perform_symmetry_on_game_state(game_state, "d2")
        tmp_result = self._cnf.get_result(tmp_game_state)
        cnf_result += self._perform_symmetry_on_cnf_result(tmp_result, "d2")
        tmp_game_state = self._perform_symmetry_on_game_state(
            self._perform_symmetry_on_game_state(game_state, "h"), "v")
        tmp_result = self._cnf.get_result(tmp_game_state)
        cnf_result += self._perform_symmetry_on_cnf_result(self._perform_symmetry_on_cnf_result(tmp_result, "h"), "v")
        return cnf_result

    def _perform_symmetry_on_game_state(self, game_state, classifier):
        game_state_after_symmetry = [0 for _ in range((self._board_size ** 2) * 2)]
        for i in range(len(game_state)):
            if game_state[i] == 1:
                player = 0
                if not (i % 2 == 0):
                    i -= 1
                    player += 1
                index = (i // 2) + 1
                coordinate = self._transform_index_to_coordinate(index)
                coordinate_after_symmetry = self._perform_symmetry_on_coordinate(coordinate[0], coordinate[1],
                                                                                 classifier)
                new_array_index = ((self._transform_coordinate_to_index(coordinate_after_symmetry[0],
                                                                        coordinate_after_symmetry[1]) - 1) * 2) + player
                game_state_after_symmetry[new_array_index] = 1
        return game_state_after_symmetry

    def _perform_symmetry_on_cnf_result(self, tmp_result, classifier):
        cnf_result_after_symmetry = []
        for tr in tmp_result:
            index = tr[1]
            coordinate = self._transform_index_to_coordinate(index)
            coordinate_after_symmetry = self._perform_symmetry_on_coordinate(coordinate[0], coordinate[1], classifier)
            index_after_symmetry = self._transform_coordinate_to_index(coordinate_after_symmetry[0],
                                                                       coordinate_after_symmetry[1])
            cnf_result_after_symmetry.append((tr[0], index_after_symmetry))
        return cnf_result_after_symmetry

    def _perform_symmetry_on_coordinate(self, x, y, classifier):
        match classifier:
            case "v":
                return self._board_size - x + 1, y
            case "h":
                return x, self._board_size - y + 1
            case "d1":
                return y, x
            case "d2":
                return self._board_size - y + 1, self._board_size - x + 1

    def _transform_index_to_coordinate(self, index):
        return ((index - 1) % self._board_size) + 1, math.ceil(index / self._board_size)

    def _transform_coordinate_to_index(self, x, y):
        return (self._board_size * y) - (self._board_size - x)
