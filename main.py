import glob
import os
import time
from datetime import datetime
from pathlib import Path

import converter

FILES_DIRECTORIES = glob.glob(str(Path(os.getcwd()).joinpath("psq").joinpath("*.psq")))
DEFAULT_BOARD_SIZE = 15
TIME_SNAPSHOT = datetime.now().strftime("%H%M%S.%f")

conv = converter.Converter(FILES_DIRECTORIES, DEFAULT_BOARD_SIZE, TIME_SNAPSHOT)

start = time.time()
conv.run()
end = time.time()

print(f"conversion of {len(FILES_DIRECTORIES)} files finished in: "
      f"{time.strftime('%H:%M:%S', time.gmtime(end - start))}")
