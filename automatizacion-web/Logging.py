import logging
from datetime import datetime
from pathlib import Path
import time

def setup_logging():
    log_filename = f"log_{datetime.now().strftime('%Y-%m-%d')}.log"
    logging_directory = Path("output/logs")
    logging_directory.mkdir(parents=True, exist_ok=True)
    log_filepath = logging_directory / log_filename

    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().addHandler(console_handler)

    logging.info("Loguer activado.")
