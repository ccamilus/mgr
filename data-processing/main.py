import glob
import os
from datetime import datetime
from pathlib import Path

import converter
import generator

time_snapshot = datetime.now().strftime("%H%M%S.%f")
default_board_size = 15
base_path = Path(os.path.dirname(os.path.abspath(__file__)))
psq_files_directories = glob.glob(str(base_path.joinpath("../data/*.psq")))

conv = converter.Converter(psq_files_directories, default_board_size, time_snapshot)
conv.run()

csv_files_directories = glob.glob(str(base_path.joinpath(f"output/{time_snapshot}/csv/*.csv")))

gen = generator.Generator(csv_files_directories, default_board_size, time_snapshot)
gen.run()
