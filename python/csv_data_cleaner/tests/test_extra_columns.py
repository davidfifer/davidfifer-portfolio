"""
Tests for validating extra‑column handling in the Cleaner.

This module verifies that the Cleaner correctly normalizes column names
and removes any columns not defined in the test‑local configuration
rules. The test uses a controlled CSV file under ``tests/data`` and a
test‑specific rules configuration under ``tests/config`` to ensure
predictable behavior.
"""

import os
import yaml

from csv_cleaner.cleaner import Cleaner


def test_extra_columns():
    """
    Ensure the Cleaner removes unexpected columns after normalization.

    This test loads a CSV file containing extra, non‑schema columns and
    applies the test‑local configuration rules. The Cleaner is expected
    to normalize column names, drop any columns not included in the
    configuration, and return a DataFrame containing only the expected
    schema fields.

    Steps
    -----
    1. Build a stable path to ``tests/data/extra_columns.csv``.
    2. Load the test‑local rules configuration from
       ``tests/config/rules.yaml``.
    3. Instantiate the Cleaner with the loaded configuration.
    4. Assert that the resulting DataFrame contains exactly the expected
       normalized columns.
    5. Assert that extra columns (e.g., ``extra1``, ``extra2``) were
       removed.

    Raises
    ------
    AssertionError
        If the Cleaner does not drop extra columns or if the resulting
        DataFrame contains unexpected fields.
    """
    # Path to the CSV file containing extra columns
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "extra_columns.csv")

    # Load test-local rules configuration
    config_path = os.path.join(test_dir, "config", "rules.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    cleaner = Cleaner(config=config)
    df = cleaner.clean(file_path)

    # Expected columns after normalization + dropping extras
    expected = {
        "user_id", "email", "age", "price", "signup_date",
        "is_active", "status", "country", "zip_code"
    }

    # Assert only expected columns remain
    assert set(df.columns) == expected

    # Assert extra columns were removed
    assert "extra1" not in df.columns
    assert "extra2" not in df.columns
