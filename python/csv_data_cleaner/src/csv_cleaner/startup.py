"""
Startup utility for initializing the csv_cleaner application.

This module provides a lightweight initialization routine that prepares
the application's runtime environment. It delegates logging setup and
any other global configuration tasks to the underlying initialization
functions within the configuration subsystem.
"""

from csv_cleaner.config.logging_setup import init_logging


def initialize():
    """
    Perform application-wide initialization routines.

    This function sets up logging and prepares any global configuration
    required before other components of the csv_cleaner package execute.
    It is intended to be called once at application startup—typically
    from the package's main entry point.

    Returns
    -------
    None
        This function does not return a value. It performs setup tasks
        that affect the application's global runtime environment.
    """
    init_logging()
