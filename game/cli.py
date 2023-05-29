import math


class Board:
    def __init__(self, board_size):
        self._board_size = board_size
        self._prepare_printable_board()

    def _prepare_printable_board(self):
        self._printable_state = [["  " if i == 64 else chr(i) for i in range(64, 80)]]
        for i in range(self._board_size):
            tmp_arr = [f" {i + 1}"] if i < 9 else [str(i + 1)]
            for j in range(self._board_size):
                tmp_arr.append("-")
            self._printable_state.append(tmp_arr)

    def print(self):
        print("       ● - human | ○ - ai")
        for row in self._printable_state:
            for el in row:
                print(el, end=" ")
            print()

    def update_board(self, x, y, player):
        self._printable_state[y + 1][x + 1] = "●" if player == 0 else "○"


class Game:
    def __init__(self, ai, board_size):
        self._game_state = [0 for _ in range(450)]
        self._current_player = 0
        self._board = Board()
        self._ai = ai
        self._board_size = board_size
        self._run = True

    def _change_player(self):
        self._current_player = (self._current_player + 1) % 2

    def _human_move(self, message):
        human_input = input(message)
        if human_input.lower() == "exit":
            self._run = False
            return
        x = ord(human_input.lower()[0]) - 97
        y = int(human_input[1:]) - 1
        print(x, y)
        state_pos = (y * self._board_size + x) * 2
        if self._game_state[state_pos] == "1" or self._game_state[state_pos + 1] == "1":
            self._human_move("wrong coordinates, try again: ")
        else:
            self._game_state[state_pos] = 1
            self._board.update_board(x, y, self._current_player)

    def _ai_move(self):
        print("AI's \"thinking\"... ")
        move = self._ai.get_best_move(self._game_state)
        x = ((move - 1) % self._board_size)
        y = math.ceil(move / self._board_size) - 1
        print(x, y)
        state_pos = ((x * self._board_size + y) * 2) + self._current_player
        self._game_state[state_pos] = 1
        self._board.update_board(x, y, self._current_player)

    def _perform_game_logic(self):
        if self._current_player == 0:
            self._human_move("write coordinates or exit: ")
        else:
            self._ai_move()
        self._change_player()

    def main_loop(self):
        while self._run:
            # os.system('cls' if os.name == 'nt' else 'clear')
            self._board.print()
            self._perform_game_logic()
