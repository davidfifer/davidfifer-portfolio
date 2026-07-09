"""
Tests for validating missing‑header detection in the Cleaner.

This module verifies that the Cleaner correctly raises a ValueError when
encountering CSV files with missing or empty column headers. The test
uses a controlled CSV file under ``tests/data`` and intentionally passes
an empty configuration to ensure header validation is performed
independently of any rule definitions.
"""

import os
import pytest

from csv_cleaner.cleaner import Cleaner


def test_missing_headers():
    """
    Ensure the Cleaner raises ValueError when a CSV file contains
    missing or empty column headers.

    This test loads a CSV file with intentionally malformed headers and
    instantiates the Cleaner with an empty configuration. The Cleaner is
    expected to perform schema validation before applying any rules and
    reject the file due to missing header names.

    Steps
    -----
    1. Build a stable path to ``tests/data/missing_headers.csv``.
    2. Instantiate the Cleaner with an empty configuration.
    3. Assert that calling ``clean()`` raises ``ValueError`` due to
       missing or invalid headers.

    Raises
    ------
    AssertionError
        If the Cleaner does not raise ValueError for missing headers.
    """
    # Path to the CSV file containing missing headers
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "missing_headers.csv")

    cleaner = Cleaner(config={})

    # Expect ValueError due to missing or empty column headers
    with pytest.raises(ValueError):
        cleaner.clean(file_path)
