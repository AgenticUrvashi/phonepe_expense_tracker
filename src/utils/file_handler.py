""" Read transaction data from a text file and write summary to a JSON file"""

import json
import logging
from pathlib import Path

logger = logging.getLogger("PhonePeTracer")

def read_text_file(file_path: Path) -> list[str]:
    ''' Read a text file and return a list of lines'''
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    else:
        logger.error(f"file not found: {file_path}")
        return []

def write_json_file(data: dict, output_path:Path) -> None:
    ''' Write data to a JSON file'''
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info(f"Data written to {output_path}")
