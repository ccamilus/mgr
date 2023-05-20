import os
from pathlib import Path


class Generator:
    def __init__(self, algorithm, default_board_size, time_snapshot, csv_directories, number_of_training_loops,
                 number_of_literals, number_of_clauses, number_of_formulas):
        self._algorithm = algorithm
        self._goal_column = (default_board_size ** 2) * 2
        self._output_path = Path(os.path.dirname(os.path.abspath(__file__))).joinpath(f"output/{time_snapshot}/cnf")
        self._csv_directories = csv_directories
        self._number_of_training_loops = number_of_training_loops
        self._number_of_literals = number_of_literals
        self._number_of_clauses = number_of_clauses
        self._number_of_formulas = number_of_formulas

    def run(self):
        for csv_directory in self._csv_directories:
            precision = self._algorithm.run(csv_directory, self._number_of_training_loops, self._number_of_literals,
                                            self._number_of_clauses, self._number_of_formulas, self._goal_column,
                                            self._output_path)
            print(f"average precision for file {Path(csv_directory).name} is {precision}%")
