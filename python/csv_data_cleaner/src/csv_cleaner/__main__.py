"""
Application startup module for the csv_cleaner package.

This module initializes the application environment and launches the
Typer-based command-line interface (CLI). It serves as the primary
entry point when executing the package via ``python -m csv_cleaner`` or
direct invocation of this file.
"""

from csv_cleaner.startup import initialize
from csv_cleaner.cli import app


def main():
    """
    Initialize the CSV Cleaner application and invoke the CLI.

    This function performs any required startup routines—such as
    configuring logging, loading environment settings, or preparing
    dependencies—before delegating execution to the Typer CLI
    application.

    Returns
    -------
    None
        This function does not return a value. It runs the CLI
        application, which handles user interaction and command
        execution.
    """
    initialize()
    app()


if __name__ == "__main__":
    main()
