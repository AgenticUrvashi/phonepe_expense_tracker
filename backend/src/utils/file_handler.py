"""File handling utilities for text, JSON, and CSV operations."""

import json
from pathlib import Path
from typing import List, Dict, Any, Union


def read_text_file(file_path: Union[str, Path]) -> List[str]:
    """Reads all lines from a text file with UTF-8 encoding."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def write_json_file(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """Writes a dictionary data structure to a JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Reads JSON data from a file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
