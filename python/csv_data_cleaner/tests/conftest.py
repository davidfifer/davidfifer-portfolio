"""
Pytest configuration and shared fixtures for the csv_cleaner test suite.

This module ensures the application's startup routines—such as logging
initialization—run once before any tests execute. It also provides
session‑scoped access to the YAML configuration file used by the
Cleaner, along with a helper fixture for loading CSV test data into
pandas DataFrames.

Directory structure relevant to these fixtures:

    csv_data_cleaner/
        src/
            csv_cleaner/
                config/
                    rules.yaml
                cli.py
                cleaner.py
                *.py
        tests/
            config/
                rules.yaml
            data/
                *.csv
            conftest.py
                test_*.py
"""

import os
import yaml
import pytest
import pandas as pd

from csv_cleaner.startup import initialize


def pytest_configure():
    """
    Run application startup initialization before any tests execute.

    This hook ensures logging and other global setup routines are
    performed once at the beginning of the pytest session. It mirrors
    the initialization performed when running the application normally.
    """
    initialize()


@pytest.fixture(scope="session")
def cfg():
    """
    Load the YAML configuration used by the Cleaner.

    This fixture provides session‑wide access to the configuration
    defined in ``csv_cleaner/config/rules.yaml``. The path is resolved
    relative to the test directory structure to ensure compatibility
    when running tests from different working directories.

    Returns
    -------
    dict
        Parsed YAML configuration as a Python dictionary.

    Raises
    ------
    FileNotFoundError
        If the configuration file cannot be located at the expected
        path.
    """
    base_dir: str = os.path.dirname(__file__)
    cfg_path = os.path.join(base_dir, "config", "rules.yaml")

    if not os.path.exists(cfg_path):
        raise FileNotFoundError(f"Config file not found at: {cfg_path}")

    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def load_csv():
    """
    Load a CSV file from ``tests/data/`` into a pandas DataFrame.

    This fixture returns a loader function that accepts a filename and
    resolves it relative to the test data directory. It is intended for
    use in tests that validate CSV cleaning behavior.

    Returns
    -------
    Callable[[str], pandas.DataFrame]
        A function that loads the specified CSV file into a DataFrame.
    """
    def _loader(filename: str):
        base_dir: str = os.path.dirname(__file__)
        csv_path = os.path.join(base_dir, "data", filename)
        return pd.read_csv(csv_path)

    return _loader
