"""
Tests for validating row‑filtering behavior in the Cleaner.

This module verifies that the Cleaner correctly applies all configured
row‑filtering rules defined in ``tests/config/rules.yaml``. The test
uses a controlled CSV file under ``tests/data`` containing a mixture of
valid and invalid rows—incorrect emails, out‑of‑range numeric values,
disallowed countries, inactive statuses, and malformed ZIP codes. The
Cleaner is expected to enforce every rule and return only the rows that
fully satisfy the configured constraints.
"""

import os
import yaml

from csv_cleaner.cleaner import Cleaner


def test_row_filters():
    """
    Ensure the Cleaner applies all row‑filtering rules and returns only
    the rows that satisfy every configured constraint.

    This test loads a CSV file containing a variety of valid and invalid
    rows. After loading the test‑local configuration, strict date
    validation is disabled to isolate row‑filtering behavior. The
    Cleaner is expected to enforce:

    - Email regex validation
    - Numeric range validation for price
    - Required column presence
    - Country membership in ``{"us", "canada"}``
    - Status equal to ``"active"``
    - ZIP code validity (non‑null, non‑coerced)

    Only rows meeting all criteria should remain.

    Steps
    -----
    1. Build a stable path to ``tests/data/row_filters.csv``.
    2. Load the test‑local rules configuration from
       ``tests/config/rules.yaml``.
    3. Disable strict date validation to isolate row‑filtering logic.
    4. Instantiate the Cleaner with the modified configuration.
    5. Run ``clean()`` to apply all row‑filtering rules.
    6. Assert that the resulting DataFrame contains only the expected
       surviving rows.

    Expected surviving rows
    -----------------------
    Rows with ``user_id`` values:

    - 1
    - 5
    - 8
    - 11

    These rows satisfy all configured rules.

    Raises
    ------
    AssertionError
        If any invalid row survives filtering or any expected row is
        removed.
    """
    # Path to the CSV file containing mixed valid/invalid rows
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "row_filters.csv")

    # Load test-local rules configuration
    config_path = os.path.join(test_dir, "config", "rules.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Disable strict date validation for this test
    config["dates"] = {"enabled": False}

    cleaner = Cleaner(config=config)
    df = cleaner.clean(file_path)

    # Expected rows after all filters applied
    expected_ids = {1, 5, 8, 11}

    # Validate final output
    assert set(df["user_id"]) == expected_ids
    assert len(df) == len(expected_ids)

    # Email regex validation
    assert df["email"].str.contains(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    ).all()

    # Price numeric range validation (0–100)
    assert df["price"].between(0, 100).all()

    # Status must be active
    assert (df["status"] == "active").all()

    # Country must be us or canada
    assert df["country"].isin(["us", "canada"]).all()
