"""
Tests for validating string‑trimming behavior in the Cleaner.

This module verifies that the Cleaner correctly trims leading and
trailing whitespace from string‑typed columns according to the
test‑local configuration rules defined in ``tests/config/rules.yaml``.
The test uses a controlled CSV file under ``tests/data`` containing
intentional whitespace around email values to ensure the trimming logic
behaves predictably.
"""

import os
import yaml

from csv_cleaner.cleaner import Cleaner


def test_trim_strings():
    """
    Ensure the Cleaner trims leading and trailing whitespace from
    configured string columns.

    This test loads a CSV file containing email values padded with
    whitespace. After loading the test‑local configuration, row‑filtering
    rules are disabled to isolate trimming behavior. The Cleaner is
    expected to apply its string‑trimming logic and return a DataFrame
    where the email column contains normalized, whitespace‑free values.

    Steps
    -----
    1. Build a stable path to ``tests/data/trim_strings.csv``.
    2. Load the test‑local rules configuration from
       ``tests/config/rules.yaml``.
    3. Disable row‑filtering rules to avoid unrelated row removal.
    4. Instantiate the Cleaner with the modified configuration.
    5. Run ``clean()`` to apply string‑trimming logic.
    6. Assert that the email column contains trimmed values.

    Expected behavior
    -----------------
    - ``email`` → `"test@example.com"` (no leading or trailing spaces)

    Raises
    ------
    AssertionError
        If the Cleaner does not trim whitespace from the email column.
    """
    # Path to the CSV file containing whitespace-padded email values
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "trim_strings.csv")

    # Load test-local rules configuration
    config_path = os.path.join(test_dir, "config", "rules.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Disable row filters to isolate trimming behavior
    if "row_filters" in config:
        config["row_filters"]["enabled"] = False

    cleaner = Cleaner(config=config)
    df = cleaner.clean(file_path)

    # The cleaner should trim leading/trailing whitespace from the email column
    assert df.loc[0, "email"] == "test@example.com"
