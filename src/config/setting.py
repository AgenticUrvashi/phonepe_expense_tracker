'''
Load environment variable from .env file safely
'''
import os
from pathlib import Path
import logging

logger = logging.getLogger("Phonepetracer")

def _load_env_file(env_path:Path) -> None:
    ''' Road .env file variables into environment'''
    try:
        if env_path.exists():
            with open(env_path,"r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Add variable to environment
                        os.environ.setdefault(key.strip(),value.strip())
    except Exception as e:
        logger.error(f"Error loading environment variable from {env_path}: {e}")


_env_path = Path(__file__).parent.parent.parent / ".env"
_load_env_file(_env_path)
BUDGET_LIMIT: float = float(os.getenv("BUDGET_LIMIT", 5000))
DATA_FILE_PATH: Path = Path(os.getenv("DATA_FILE_PATH","data/transactions.txt"))
OUTPUT_JSON_PATH: Path = Path((os.getenv("OUTPUT_JSON_PATH","data/summary.json")))
LOG_FILE_PATH: Path = Path(os.getenv("LOG_FILE_PATH","logs/tracker.log"))



# if __name__ == "__main__":
#     print(BUDGET_LIMIT)
#     print(DATA_FILE_PATH)
#     print(OUTPUT_JSON_PATH)
#     print(LOG_FILE_PATH)