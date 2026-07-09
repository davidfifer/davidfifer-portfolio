"""
Tests for validating strict date‑parsing behavior in the Cleaner.

This module verifies that the Cleaner correctly raises a ValueError when
encountering invalid or non‑parseable date values. The test uses a
controlled CSV file under ``tests/data`` and a test‑local rules
configuration under ``tests/config``. Row‑filtering rules are disabled
to ensure the test focuses solely on date validation.
"""

import os
import yaml
import pytest

from csv_cleaner.cleaner import Cleaner


def test_invalid_dates():
    """
    Ensure the Cleaner raises ValueError when date columns contain
    invalid or non‑parseable values.

    This test loads a CSV file containing intentionally malformed date
    strings and applies the test‑local configuration. Row‑filtering
    rules are disabled so that only date validation behavior is tested.
    The Cleaner is expected to enforce strict date parsing and reject
    the file.

    Steps
    -----
    1. Build a stable path to ``tests/data/invalid_dates.csv``.
    2. Load the test‑local rules configuration from
       ``tests/config/rules.yaml``.
    3. Disable row‑filtering rules to isolate date validation.
    4. Instantiate the Cleaner with the modified configuration.
    5. Assert that calling ``clean()`` raises ``ValueError`` due to
       invalid date values.

    Raises
    ------
    AssertionError
        If the Cleaner does not raise ValueError for invalid dates.
    """
    # Path to the CSV file containing invalid date values
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "invalid_dates.csv")

    # Load test-local rules configuration
    config_path = os.path.join(test_dir, "config", "rules.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Disable row filters to isolate date validation behavior
    if "row_filters" in config:
        config["row_filters"]["enabled"] = False

    cleaner = Cleaner(config=config)

    # Expect ValueError due to invalid date values
    with pytest.raises(ValueError):
        cleaner.clean(file_path)
