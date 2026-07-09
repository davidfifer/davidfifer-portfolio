"""
Logging configuration module for the CSV Cleaner application.

This module defines a portable log file location, ensures the directory
exists, and provides a dictionary-based logging configuration compatible
with `logging.config.dictConfig`. It initializes the root logger with both
console and file handlers for consistent application-wide logging.
"""

import logging.config
from pathlib import Path

# Portable, safe log file path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_FILE = PROJECT_ROOT / "logs" / "app.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

#: Dictionary-based logging configuration for the application.
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    # -------------------------
    # FORMATTERS
    # -------------------------
    "formatters": {
        "defaultFormatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M",
        }
    },

    # -------------------------
    # HANDLERS
    # -------------------------
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "defaultFormatter",
            "stream": "ext://sys.stdout",
        },
        "fileHandler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "defaultFormatter",
            "filename": str(LOG_FILE),
            "mode": "a",
        },
    },

    # -------------------------
    # LOGGERS
    # -------------------------
    "loggers": {},

    # -------------------------
    # ROOT LOGGER
    # -------------------------
    "root": {
        "level": "DEBUG",
        "handlers": ["consoleHandler", "fileHandler"],
    },
}

# Apply logging configuration at import time
logging.config.dictConfig(LOGGING_CONFIG)
