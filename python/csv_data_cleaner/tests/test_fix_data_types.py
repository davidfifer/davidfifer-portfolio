"""
Tests for validating dtype‑coercion behavior in the Cleaner.

This module verifies that the Cleaner correctly enforces data‑type
normalization rules defined in the test‑local configuration under
``tests/config``. The test uses a controlled CSV file containing mixed
types and malformed values to ensure the Cleaner applies the expected
coercions for integer, float, boolean, and datetime fields.
"""

import os
import yaml

from csv_cleaner.cleaner import Cleaner


def test_fix_data_types():
    """
    Ensure the Cleaner coerces column data types according to the
    configuration rules.

    This test loads a CSV file containing intentionally inconsistent
    data types and applies the test‑local rules configuration. The
    Cleaner is expected to normalize each column to its configured
    dtype, using pandas' nullable dtypes where appropriate.

    Steps
    -----
    1. Build a stable path to ``tests/data/fix_data_types.csv``.
    2. Load the test‑local rules configuration from
       ``tests/config/rules.yaml``.
    3. Instantiate the Cleaner with the loaded configuration.
    4. Run ``clean()`` to apply dtype coercion.
    5. Assert that each column's dtype matches the expected normalized
       pandas dtype.

    Expected dtypes
    ---------------
    - ``user_id`` → ``Int64`` (nullable integer)
    - ``age`` → ``Int64`` (nullable integer)
    - ``price`` → ``float64``
    - ``signup_date`` → ``datetime64[ns]``
    - ``is_active`` → ``bool``

    Raises
    ------
    AssertionError
        If any column does not match its expected dtype after cleaning.
    """
    # Path to the CSV file containing mixed-type values
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "fix_data_types.csv")

    # Load test-local rules configuration
    config_path = os.path.join(test_dir, "config", "rules.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    cleaner = Cleaner(config=config)
    df = cleaner.clean(file_path)

    # Assert dtype coercion results
    assert df["user_id"].dtype == "Int64"
    assert df["age"].dtype == "Int64"
    assert df["price"].dtype == "float64"
    assert df["signup_date"].dtype == "datetime64[ns]"
    assert df["is_active"].dtype == "bool"
