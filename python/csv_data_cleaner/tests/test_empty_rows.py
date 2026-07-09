"""
Tests for validating empty‑row handling in the Cleaner.

This module verifies that the Cleaner correctly removes rows that are
either fully empty or contain only whitespace. The test uses a
controlled CSV file under ``tests/data`` and a test‑local rules
configuration under ``tests/config``. Certain row‑filtering rules are
disabled to ensure the test focuses solely on empty‑row removal.
"""

import os
import yaml

from csv_cleaner.cleaner import Cleaner


def test_empty_rows():
    """
    Ensure the Cleaner removes empty and whitespace‑only rows.

    This test loads a CSV file containing intentionally empty and
    whitespace‑only rows, then applies a modified configuration where
    unrelated row‑filtering rules are disabled. The Cleaner is expected
    to return a DataFrame containing only the valid rows.

    Steps
    -----
    1. Build a stable path to ``tests/data/empty_rows.csv``.
    2. Load the test‑local rules configuration from
       ``tests/config/rules.yaml``.
    3. Disable unrelated row‑filtering rules (``keep_if``) to isolate
       empty‑row removal behavior.
    4. Instantiate the Cleaner with the modified configuration.
    5. Assert that the cleaned DataFrame contains exactly two valid rows.
    6. Assert that the remaining rows contain the expected ``user_id``
       values.

    Raises
    ------
    AssertionError
        If the Cleaner does not remove empty rows or if the resulting
        DataFrame does not contain the expected values.
    """
    # Path to the CSV file containing empty and whitespace-only rows
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "empty_rows.csv")

    # Load test-local rules configuration
    config_path = os.path.join(test_dir, "config", "rules.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Disable unrelated row-filtering rules
    config["row_filters"]["keep_if"] = {}

    cleaner = Cleaner(config=config)
    df = cleaner.clean(file_path)

    # Assert that empty / whitespace-only rows were removed
    assert len(df) == 2

    # Assert the remaining rows are valid
    assert df.loc[0, "user_id"] == 1
    assert df.loc[2, "user_id"] == 2
