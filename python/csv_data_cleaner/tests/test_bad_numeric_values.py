"""
Tests for validating strict numeric handling in the Cleaner.

This module verifies that the Cleaner correctly raises a ValueError
when encountering invalid numeric values in CSV files. The test uses
the test-local configuration located under ``tests/config/rules.yaml``
and a purposely malformed CSV file under ``tests/data``.
"""

import os
import yaml
import pytest
from csv_cleaner.cleaner import Cleaner


def test_bad_numeric_values():
    """
    Ensure the Cleaner raises ValueError when numeric columns contain
    invalid (non-numeric) values.

    This test loads the test-specific rules configuration and applies
    it to a CSV file containing intentionally malformed numeric fields.
    The Cleaner is expected to enforce strict numeric validation and
    reject the file.

    Steps
    -----
    1. Build a stable path to ``tests/data/bad_numeric_values.csv``.
    2. Load the test-local YAML rules from ``tests/config/rules.yaml``.
    3. Instantiate the Cleaner with the loaded configuration.
    4. Assert that calling ``clean()`` raises ``ValueError``.

    Raises
    ------
    AssertionError
        If the Cleaner does not raise ValueError for invalid numeric
        values.
    """
    # Path to the malformed CSV file
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "bad_numeric_values.csv")

    # Load test-local rules configuration
    config_path = os.path.join(test_dir, "config", "rules.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    cleaner = Cleaner(config=config)

    # Expect ValueError because numeric columns contain invalid values
    with pytest.raises(ValueError):
        cleaner.clean(file_path)
