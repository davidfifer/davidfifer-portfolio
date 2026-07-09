"""
Tests for validating required‑column enforcement in the Cleaner.

This module verifies that the Cleaner correctly raises a ValueError when
a CSV file is missing one or more required columns *after normalization*.
The test uses a controlled CSV file under ``tests/data`` and a
test‑local rules configuration under ``tests/config`` to ensure
predictable behavior.
"""

import os
import yaml
import pytest

from csv_cleaner.cleaner import Cleaner


def test_missing_required_columns():
    """
    Ensure the Cleaner raises ValueError when required columns are
    missing after header normalization.

    This test loads a CSV file that intentionally omits one or more
    required fields. After loading the test‑local configuration, the
    Cleaner is expected to normalize column names, validate the schema,
    and reject the file due to missing required columns.

    Steps
    -----
    1. Build a stable path to ``tests/data/missing_required_columns.csv``.
    2. Load the test‑local rules configuration from
       ``tests/config/rules.yaml``.
    3. Instantiate the Cleaner with the loaded configuration.
    4. Assert that calling ``clean()`` raises ``ValueError`` because
       required columns are missing after normalization.

    Raises
    ------
    AssertionError
        If the Cleaner does not raise ValueError when required columns
        are missing.
    """
    # Path to the CSV file missing required columns
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "missing_required_columns.csv")

    # Load test-local rules configuration
    config_path = os.path.join(test_dir, "config", "rules.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    cleaner = Cleaner(config=config)

    # Expect ValueError because required columns are missing AFTER normalization
    with pytest.raises(ValueError):
        cleaner.clean(file_path)
