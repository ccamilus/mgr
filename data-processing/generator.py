class Generator:
    def __init__(self, csv_files_directories, default_board_size, time_snapshot):
        self._csv_files_directories = csv_files_directories
        self._goal_column = (default_board_size ** 2) * 2
        self._time_snapshot = time_snapshot

    def run(self):
        for csv_file in self._csv_files_directories:
            pass
