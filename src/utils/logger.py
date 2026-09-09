import logging
from src.config.setting import LOG_FILE_PATH

def setup_logger() -> logging.Logger:
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("PhonePeTracer")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # write logs to file
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # stream handler: print logs to console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# if __name__ == "__main__":
#     logger = setup_logger()
#     logger.info("Logger setup complete") 