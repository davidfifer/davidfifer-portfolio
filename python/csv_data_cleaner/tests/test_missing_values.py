"""
Tests for validating missing‑value handling in the Cleaner.

This module verifies that the Cleaner correctly fills missing numeric
values according to the test‑local configuration rules defined in
``tests/config/rules.yaml``. The test uses a controlled CSV file under
``tests/data`` containing intentionally missing values to ensure the
Cleaner applies the expected fill‑strategies for numeric fields.
"""

import os
import yaml

from csv_cleaner.cleaner import Cleaner


def test_missing_values():
    """
    Ensure the Cleaner fills missing numeric values according to the
    configuration rules.

    This test loads a CSV file containing missing numeric fields and
    applies the test‑local configuration. Row‑filtering rules and strict
    date validation are disabled to isolate missing‑value behavior. The
    Cleaner is expected to fill missing numeric values using the
    configured defaults or strategies (e.g., median, explicit values).

    Steps
    -----
    1. Build a stable path to ``tests/data/missing_values.csv``.
    2. Load the test‑local rules configuration from
       ``tests/config/rules.yaml``.
    3. Disable row‑filtering rules to avoid unintended row removal.
    4. Disable strict date validation to prevent unrelated failures.
    5. Instantiate the Cleaner with the modified configuration.
    6. Assert that missing numeric values were filled correctly.

    Expected behavior
    -----------------
    - ``age`` missing value → filled with ``40``
    - ``price`` missing value → filled with ``15.5``

    Raises
    ------
    AssertionError
        If missing numeric values are not filled as expected.
    """
    # Path to the CSV file containing missing numeric values
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "missing_values.csv")

    # Load test-local rules configuration
    config_path = os.path.join(test_dir, "config", "rules.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Disable row filters to isolate missing-value behavior
    if "row_filters" in config:
        config["row_filters"]["enabled"] = False

    # Disable strict date validation
    if "dates" in config:
        config["dates"]["strict"] = False

    cleaner = Cleaner(config=config)
    df = cleaner.clean(file_path)

    # Assert missing numeric values were filled
    assert df.loc[0, "age"] == 40
    assert df.loc[1, "price"] == 15.5
