"""
Tests for validating duplicate‑row handling in the Cleaner.

This module verifies that the Cleaner correctly identifies and removes
duplicate rows according to the test‑specific configuration rules.
The test uses a controlled CSV file under ``tests/data`` and a
test‑local rules configuration under ``tests/config``. Certain
row‑filtering rules are explicitly disabled to ensure the test focuses
solely on duplicate detection.
"""

import os
import yaml

from csv_cleaner.cleaner import Cleaner


def test_duplicates():
    """
    Ensure the Cleaner correctly removes duplicate rows when duplicate
    detection rules are applied.

    This test loads a CSV file containing intentional duplicate rows and
    applies a modified configuration where unrelated row‑filtering rules
    are disabled. The Cleaner is expected to return a DataFrame with
    only the unique rows preserved.

    Steps
    -----
    1. Build a stable path to ``tests/data/duplicates.csv``.
    2. Load the test‑local rules configuration from
       ``tests/config/rules.yaml``.
    3. Disable unrelated row‑filtering rules (``keep_if`` and
       ``drop_if_equals``) to isolate duplicate‑removal behavior.
    4. Instantiate the Cleaner with the modified configuration.
    5. Assert that the cleaned DataFrame contains exactly two rows.

    Raises
    ------
    AssertionError
        If the Cleaner does not return the expected number of rows.
    """
    # Path to the CSV file containing duplicates
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "duplicates.csv")

    # Load test-local rules configuration
    config_path = os.path.join(test_dir, "config", "rules.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Disable unrelated row-filtering rules
    config["row_filters"]["keep_if"] = {}
    config["row_filters"]["drop_if_equals"] = {}

    cleaner = Cleaner(config=config)
    df = cleaner.clean(file_path)

    assert len(df) == 2
