import csv
import os
from pathlib import Path

import utils as u

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
BOARD_SIZE = 15


class CsvFieldShifter:
    @staticmethod
    def shift(base_field, target_field):
        shifted_rows = []
        x = u.transform_index_to_coordinate(target_field, BOARD_SIZE)[0] - \
            u.transform_index_to_coordinate(base_field, BOARD_SIZE)[0]
        y = u.transform_index_to_coordinate(target_field, BOARD_SIZE)[1] - \
            u.transform_index_to_coordinate(base_field, BOARD_SIZE)[1]
        try:
            with open(BASE_DIR.joinpath(f"csv/main/{base_field}.csv"), "r") as csv_file:
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
                                tmp_x, tmp_y = u.transform_index_to_coordinate(field, BOARD_SIZE)
                                if 0 < tmp_x + x <= BOARD_SIZE and 0 < tmp_y + y <= BOARD_SIZE:
                                    corrupted_fields.append(
                                        (u.transform_coordinate_to_index(tmp_x + x, tmp_y + y, BOARD_SIZE), player))
                        shifted_row = [0 for _ in range((BOARD_SIZE ** 2) * 2)]
                        shifted_row.append(decision_value)
                        for field in corrupted_fields:
                            shifted_row[((field[0] - 1) * 2) + field[1]] = 1
                        shifted_rows.append(shifted_row)
        except FileNotFoundError:
            print(f"File with base field {base_field} not found")
        else:
            with open(BASE_DIR.joinpath(f"csv/main/{target_field}.csv"), "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(shifted_rows)


def main():
    CsvFieldShifter.shift(64, 80)
    CsvFieldShifter.shift(109, 95)
    CsvFieldShifter.shift(110, 96)
    CsvFieldShifter.shift(63, 79)
    CsvFieldShifter.shift(108, 94)


if __name__ == "__main__":
    main()
