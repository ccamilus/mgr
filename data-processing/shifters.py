import csv
import os
from pathlib import Path

import utils as u


class CsvShifter:
    @staticmethod
    def shift(base_field_path, target_field_path, board_size):
        try:
            base_field = int(Path(base_field_path).stem)
            target_field = int(Path(target_field_path).stem)
        except ValueError:
            print("Filename must be an integer, eg. 113.csv.")
        else:
            shifted_rows = []
            x = u.transform_index_to_coordinate(target_field, board_size)[0] - \
                u.transform_index_to_coordinate(base_field, board_size)[0]
            y = u.transform_index_to_coordinate(target_field, board_size)[1] - \
                u.transform_index_to_coordinate(base_field, board_size)[1]
            try:
                with open(base_field_path, "r") as csv_file:
                    for row_index, row in enumerate(csv_file):
                        if row_index == 0:
                            shifted_rows.append(row.strip().split(","))
                        else:
                            corrupted_fields = []
                            not_shifted_row = list(map(int, row.strip().split(",")))
                            decision_value = not_shifted_row[-1]
                            not_shifted_row.pop()
                            for column_index, column_value in enumerate(not_shifted_row):
                                if column_value == 1:
                                    player = 0 if column_index % 2 == 0 else 1
                                    field = ((column_index - player) // 2) + 1
                                    tmp_x, tmp_y = u.transform_index_to_coordinate(field, board_size)
                                    if 0 < tmp_x + x <= board_size and 0 < tmp_y + y <= board_size:
                                        corrupted_fields.append(
                                            (u.transform_coordinate_to_index(tmp_x + x, tmp_y + y, board_size), player))
                            shifted_row = [0 for _ in range((board_size ** 2) * 2)]
                            shifted_row.append(decision_value)
                            for field in corrupted_fields:
                                shifted_row[((field[0] - 1) * 2) + field[1]] = 1
                            shifted_rows.append(shifted_row)
            except FileNotFoundError:
                print(f"File {base_field_path} not found.")
            else:
                if not os.path.exists(Path(target_field_path).parent):
                    os.makedirs(Path(target_field_path).parent)
                with open(target_field_path, "w", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerows(shifted_rows)
