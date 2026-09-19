"""Logger configuration for PhonePe Expense Tracker."""

import logging
import sys

def setup_logger(name: str = "PhonePeTracker") -> logging.Logger:
    """Configures and returns a standard application logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger
