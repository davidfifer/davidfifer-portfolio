"""
Centralized logging setup for the CSV Cleaner application.

This module provides a single function, `init_logging()`, which applies the
dictionary-based logging configuration defined in `logging_config.py`. It is
safe to call multiple times; the configuration will only be applied once.
"""

import logging
import logging.config

from csv_cleaner.config.logging_config import LOGGING_CONFIG

_LOGGING_INITIALIZED = False


def init_logging():
    """
    Initialize application-wide logging using the project's dictConfig.

    This function applies the logging configuration exactly once. Subsequent
    calls have no effect, ensuring that tests, CLI commands, and internal
    modules can safely invoke it without causing duplicate handlers or
    reconfigured loggers.
    """
    global _LOGGING_INITIALIZED

    if not _LOGGING_INITIALIZED:
        logging.config.dictConfig(LOGGING_CONFIG)
        _LOGGING_INITIALIZED = True
