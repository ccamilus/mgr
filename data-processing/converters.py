import glob
import os
from pathlib import Path

import csv
import utils as u

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
BOARD_SIZE = 15


class MainConverter:
    def _prepare_files(self):
        target_fields = []
        if not os.path.exists(BASE_DIR.joinpath("csv/main")):
            os.makedirs(BASE_DIR.joinpath("csv/main"))
        oddity_bonus = 0 if BOARD_SIZE % 2 == 0 else 1
        center = (BOARD_SIZE // 2) + oddity_bonus
        header_row = []
        for i in range(1, BOARD_SIZE ** 2 + 1):
            header_row.append(f"0player_field{i}")
            header_row.append(f"1player_field{i}")
        header_row.append(f"player_decision")
        for i in range(1, center + 1):
            for j in range(1, i + 1):
                field = u.transform_coordinate_to_index(j, i, BOARD_SIZE)
                target_fields.append(field)
                with open(BASE_DIR.joinpath(f"csv/main/{field}.csv"), "w", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(header_row)
        return target_fields

    def _get_moves(self, file_directory):
        moves = []
        with open(file_directory, "r") as file:
            data = [line.rstrip('\n') for line in file]
        if data:
            try:
                board_sizes = data[0].split(",")[0].split()[1].split("x")
            except IndexError:
                pass
            else:
                if board_sizes[0] == board_sizes[1] and int(board_sizes[0]) == BOARD_SIZE:
                    for i in range(1, len(data)):
                        line = data[i].split(",")
                        if len(line) == 3 and all(_.isdigit() for _ in line):
                            if 0 < int(line[0]) <= BOARD_SIZE and 0 < int(line[1]) <= BOARD_SIZE:
                                moves.append((int(line[0]), int(line[1])))
                            else:
                                moves = None
                                break
                    if moves and len(moves) != len(set(moves)):
                        moves = None
        return moves

    def _perform_symmetry(self, moves):
        tmp_board_state = []
        tmp_game = []
        game_after_symmetry = []
        for move in moves:
            tmp_game.append((tmp_board_state.copy(), move))
            tmp_board_state.append(move)
        for tmp_state in tmp_game:
            classifiers = self._get_classifiers(tmp_state[1][0], tmp_state[1][1]).split(",")
            decision = tmp_state[1]
            state = tmp_state[0]
            for classifier in classifiers:
                decision = self._perform_coordinates_transformation(decision[0], decision[1], classifier)
                for i in range(len(state)):
                    state[i] = self._perform_coordinates_transformation(state[i][0], state[i][1], classifier)
            game_after_symmetry.append((state.copy(), decision))
        return game_after_symmetry

    def _get_classifiers(self, x, y):
        board_center = BOARD_SIZE // 2
        oddity_bonus = 0
        if not BOARD_SIZE % 2 == 0:
            oddity_bonus = 1
            if y == board_center + oddity_bonus:
                return "t" if x <= board_center + oddity_bonus else "v"
            if x == board_center + oddity_bonus:
                if y < board_center + oddity_bonus:
                    return "d1"
                elif y > board_center + oddity_bonus:
                    return "d2"
        if x <= board_center and y <= board_center:
            if y >= x:
                return "t"
            else:
                return "d1"
        if x > board_center + oddity_bonus and y <= board_center:
            if y > BOARD_SIZE - x:
                return "v"
            else:
                return "v,d1"
        if x > board_center + oddity_bonus and y > board_center + oddity_bonus:
            if y >= x:
                return "d2"
            else:
                return "h,v"
        if x <= board_center and y > board_center + oddity_bonus:
            if y > BOARD_SIZE - x + 1:
                return "h,d1"
            else:
                return "h"

    def _perform_coordinates_transformation(self, x, y, classifier):
        match classifier:
            case "v":
                return BOARD_SIZE - x + 1, y
            case "h":
                return x, BOARD_SIZE - y + 1
            case "d1":
                return y, x
            case "d2":
                return BOARD_SIZE - y + 1, BOARD_SIZE - x + 1
            case "t":
                return x, y

    def _update_files(self, game_coord, target_fields):
        game_ind = []
        for state in game_coord:
            decision = u.transform_coordinate_to_index(state[1][0], state[1][1], BOARD_SIZE)
            current_state = []
            for i in range(len(state[0])):
                current_state.append(u.transform_coordinate_to_index(state[0][i][0], state[0][i][1], BOARD_SIZE))
            game_ind.append((current_state.copy(), decision))
        for state in game_ind:
            row = []
            for i in range(1, (BOARD_SIZE ** 2) + 1):
                if i in state[0]:
                    if state[0].index(i) % 2 == 0:
                        row.append(1)
                        row.append(0)
                    else:
                        row.append(0)
                        row.append(1)
                else:
                    row.append(0)
                    row.append(0)
            for field in target_fields:
                decision_value = 1 if field == state[1] else 0
                csv_row = row.copy()
                csv_row.append(decision_value)
                with open(BASE_DIR.joinpath(f"csv/main/{field}.csv"), "a", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(csv_row)

    def convert(self):
        psq_files_directories = glob.glob(str(BASE_DIR.joinpath("psq/main/*.psq")))
        target_fields = self._prepare_files()
        for file_directory in psq_files_directories:
            moves = self._get_moves(file_directory)
            if moves:
                game = self._perform_symmetry(moves)
                self._update_files(game, target_fields)


class EvaluationConverter:
    def _get_game_state_rows(self, moves):
        game_states = [(moves[:i], 1 if len(moves) % 2 == 0 else 0) for i in range(8, len(moves) + 1)]
        game_state_rows = []
        for game_state in game_states:
            row = []
            for i in range(1, (BOARD_SIZE ** 2) + 1):
                if i in game_state[0]:
                    if game_state[0].index(i) % 2 == 0:
                        row.append(1)
                        row.append(0)
                    else:
                        row.append(0)
                        row.append(1)
                else:
                    row.append(0)
                    row.append(0)
            row.append(game_state[1])
            game_state_rows.append(row)
        return game_state_rows

    def _get_moves(self, file_directory):
        moves = []
        with open(file_directory, "r") as file:
            data = [line.rstrip('\n') for line in file]
        if data:
            try:
                board_sizes = data[0].split(",")[0].split()[1].split("x")
            except IndexError:
                pass
            else:
                if board_sizes[0] == board_sizes[1] and int(board_sizes[0]) == BOARD_SIZE:
                    for i in range(1, len(data)):
                        line = data[i].split(",")
                        if len(line) == 3 and all(_.isdigit() for _ in line):
                            if 0 < int(line[0]) <= BOARD_SIZE and 0 < int(line[1]) <= BOARD_SIZE:
                                moves.append(u.transform_coordinate_to_index(int(line[0]), int(line[1]), BOARD_SIZE))
                            else:
                                moves = None
                                break
                    if (moves and len(moves) != len(set(moves))) or len(moves) == BOARD_SIZE ** 2:
                        moves = None
        return moves

    def convert(self):
        game_state_rows = []
        psq_files_directories = glob.glob(str(BASE_DIR.joinpath("psq/evaluation/*.psq")))
        for file_directory in psq_files_directories:
            moves = self._get_moves(file_directory)
            if moves:
                game_state_rows.extend(self._get_game_state_rows(moves))
        if game_state_rows:
            header_row = []
            for i in range(1, BOARD_SIZE ** 2 + 1):
                header_row.append(f"0player_field{i}")
                header_row.append(f"1player_field{i}")
            header_row.append(f"winner")
            if not os.path.exists(BASE_DIR.joinpath("csv/evaluation")):
                os.makedirs(BASE_DIR.joinpath("csv/evaluation"))
            with open(BASE_DIR.joinpath("csv/evaluation/evaluation.csv"), "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header_row)
                writer.writerows(game_state_rows)


def main():
    mc = MainConverter()
    mc.convert()
    ec = EvaluationConverter()
    ec.convert()


if __name__ == "__main__":
    main()
