import glob
import os
import time
from datetime import datetime
from pathlib import Path

import converter
import generator
from algorithms.lpdum import FormulaGenerationAlgorithm

time_snapshot = datetime.now().strftime("%H%M%S.%f")
default_board_size = 15
files_directories = glob.glob(str(Path(os.path.dirname(os.path.abspath(__file__))).joinpath("../data/*.psq")))
conv = converter.Converter(files_directories, default_board_size, time_snapshot)
start = time.time()
conv.run()
end = time.time()
print(f"conversion of {len(files_directories)} files finished in: "
      f"{time.strftime('%H:%M:%S', time.gmtime(end - start))}")
number_of_training_loops = 20
number_of_literals = 3
number_of_clauses = 10
number_of_formulas = 100
csv_directories = glob.glob(
    str(Path(os.path.dirname(os.path.abspath(__file__))).joinpath(f"output/{time_snapshot}/csv/*.csv")))
gen = generator.Generator(FormulaGenerationAlgorithm(), default_board_size, time_snapshot, csv_directories,
                          number_of_training_loops, number_of_literals, number_of_clauses, number_of_formulas)
start = time.time()
gen.run()
end = time.time()
print(f"generation of {len(csv_directories)} files finished in: "
      f"{time.strftime('%H:%M:%S', time.gmtime(end - start))}")
