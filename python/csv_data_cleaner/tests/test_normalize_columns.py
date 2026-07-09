"""
Tests for validating column‑name normalization in the Cleaner.

This module verifies that the Cleaner correctly normalizes messy,
inconsistent, or non‑standard CSV header names. The test uses a
controlled CSV file under ``tests/data`` containing intentionally
irregular column names to ensure the normalization logic behaves
predictably when no configuration rules are supplied.
"""

import os

from csv_cleaner.cleaner import Cleaner


def test_normalize_columns():
    """
    Ensure the Cleaner normalizes column names into a consistent,
    schema‑friendly format.

    This test loads a CSV file containing intentionally inconsistent
    header names—mixed casing, spaces, punctuation, and other
    irregularities. The Cleaner is instantiated with an empty
    configuration so that only the built‑in normalization logic is
    exercised. After cleaning, the resulting DataFrame is expected to
    contain normalized column names such as ``user_id``, ``emailaddress``,
    ``signup_date``, and ``zipcode``.

    Steps
    -----
    1. Build a stable path to ``tests/data/normalize_columns.csv``.
    2. Instantiate the Cleaner with an empty configuration.
    3. Run ``clean()`` to apply column‑name normalization.
    4. Assert that expected normalized column names are present.

    Expected normalized columns
    ---------------------------
    - ``user_id``
    - ``emailaddress``
    - ``age``
    - ``price``
    - ``signup_date``
    - ``is_active``
    - ``status``
    - ``country``
    - ``zipcode``

    Raises
    ------
    AssertionError
        If any expected normalized column name is missing.
    """
    # Path to the CSV file containing irregular column names
    test_dir: str = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "normalize_columns.csv")

    cleaner = Cleaner(config={})

    # Expect the cleaner to normalize column names correctly
    df = cleaner.clean(file_path)

    # Example assertions — adjust based on your expected normalized output
    assert "user_id" in df.columns
    assert "emailaddress" in df.columns
    assert "age" in df.columns
    assert "price" in df.columns
    assert "signup_date" in df.columns
    assert "is_active" in df.columns
    assert "status" in df.columns
    assert "country" in df.columns
    assert "zipcode" in df.columns
