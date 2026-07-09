"""
CSV cleaning pipeline implementation.

This module defines the `Cleaner` class, which applies a configurable,
multi‑stage cleaning process to CSV files using pandas. Supported cleaning
operations include column normalization, missing‑value handling, data‑type
fixing, string trimming, duplicate removal, and row‑level filtering.

Each cleaning step is controlled by a configuration dictionary, allowing
fine‑grained customization of behavior.
"""

import re
import logging
import pandas as pd

from pandas import DataFrame
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Cleaner:
    """
    Apply a configurable cleaning pipeline to CSV data.

    Parameters
    ----------
    config : dict
        Dictionary containing cleaning rules. Each cleaning step reads from
        its corresponding section (e.g., `normalize_columns`, `fill_missing`,
        `dtypes`, `trim_strings`, `remove_duplicates`, `row_filters`).

    Attributes
    ----------
    config : dict
        The full configuration dictionary used to control cleaning behavior.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def clean(self, file_path: str) -> DataFrame:
        """
        Run the full cleaning pipeline on a CSV file or DataFrame.

        This method loads the input into a DataFrame, validates its structure,
        and applies all configured cleaning steps in a deterministic order:

        1. Normalize column names
        2. Validate headers and drop extra columns
        3. Trim string fields
        4. Remove empty rows
        5. Validate numeric fields
        6. Optionally enforce data types
        7. Fill missing values when present
        8. Validate date fields
        9. Remove duplicate rows
        10. Apply row‑level filters

        The pipeline ensures that structural issues (missing headers, invalid
        numeric values, malformed dates) are detected early and surfaced as
        exceptions before any transformations occur.

        Parameters
        ----------
        file_path : str or DataFrame
            Path to the CSV file to clean, or an existing DataFrame. When a
            DataFrame is provided, it is copied and used directly.

        Returns
        -------
        DataFrame
            A fully cleaned DataFrame after all pipeline steps have been applied.

        Raises
        ------
        ValueError
            If column headers are missing or empty, numeric validation fails,
            or date validation fails.
        pd.errors.ParserError
            If the CSV cannot be parsed.
        FileNotFoundError
            If the provided file path does not exist.
        """
        logger.info("Starting cleaning pipeline for file %s", file_path)

        # If the input is a DataFrame, use it directly
        if isinstance(file_path, pd.DataFrame):
            df = file_path.copy()
        else:
            try:
                df = pd.read_csv(file_path)
            except (pd.errors.ParserError, FileNotFoundError):
                logger.error("Failed to read CSV file %s", file_path, exc_info=True)
                raise

        # Check for missing headers
        bad_headers = [
            col for col in df.columns
            if col is None
               or str(col).strip() == ""
               or str(col).startswith("Unnamed:")
        ]

        if bad_headers:
            raise ValueError("Missing or empty column headers")

        logger.debug("Loaded CSV; initial shape: %s", df.shape)

        # 1. Column structure
        df = self._normalize_columns(df)
        df = self._validate_headers(df)
        df = self._drop_extra_columns(df)

        # 2. String cleanup before emptiness checks
        df = self._trim_strings(df)

        # 3. Remove empty rows early
        df = self._remove_empty_rows(df)

        # 4. Validate numeric BEFORE any transformation
        self._validate_numeric(df)

        # 5. Fix data types ONLY if dtype enforcement is explicitly enabled
        dtypes_cfg = self.config.get("dtypes", {})
        if dtypes_cfg.get("enabled", False):
            df = self._fix_data_types(df)

        # 6. Fill missing values ONLY if missing values exist
        if df.isna().any().any():
            df = self._fill_missing_values(df)

        # 7. Validate dates BEFORE any transformation
        df = self._validate_dates(df)

        # 8. Remove duplicates
        df = self._remove_duplicates(df)

        # 9. Apply row filters
        df = self._apply_row_filters(df)

        logger.info("Cleaning pipeline completed successfully")
        logger.debug("Final DataFrame shape: %s", df.shape)
        return df

    def _normalize_columns(self, df: DataFrame) -> DataFrame:
        """
        Normalize column names according to the configured normalization rules.

        This method applies a deterministic sequence of transformations to each
        column name to ensure structural consistency across input files. The
        normalization process includes:

        - Lowercasing all column names
        - Stripping leading and trailing whitespace
        - Replacing whitespace with underscores
        - Removing non‑alphanumeric characters (except underscores)
        - Collapsing repeated underscores
        - Prefixing names that begin with digits (e.g., ``"123"`` → ``"col_123"``)
        - Applying alias mappings when configured

        Normalization can be disabled via the ``normalize_columns.enabled`` flag
        in the configuration. When disabled, the DataFrame is returned unchanged.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame whose column names will be normalized.

        Returns
        -------
        DataFrame
            A copy of the input DataFrame with normalized column names.

        Notes
        -----
        Alias mappings are applied *after* normalization. This ensures that
        inconsistent raw headers (e.g., ``"E‑Mail"`` vs ``"email"``) resolve to
        the same canonical name when an alias map is provided.
        """
        logger.debug("Normalizing column names")

        norm_cfg = self.config.get("normalize_columns", {})
        if not norm_cfg.get("enabled", True):
            logger.debug("Column normalization disabled")
            return df

        alias_map = norm_cfg.get("alias_map", {}) or {}

        def normalize(name: str) -> str:
            name = name.strip().lower()
            name = re.sub(r"\s+", "_", name)
            name = re.sub(r"[^\w_]", "", name)
            name = re.sub(r"_+", "_", name)
            if re.match(r"^\d", name):
                name = f"col_{name}"
            return name

        df_copy = df.copy()
        normalized = [normalize(col) for col in df_copy.columns]

        if alias_map:
            normalized = [alias_map.get(col, col) for col in normalized]

        df_copy.columns = normalized
        logger.debug("Column name normalization completed")
        return df_copy

    def _validate_headers(self, df):
        """
        Validate column headers according to the configured header rules.

        This method enforces structural requirements on the DataFrame's column
        headers before any downstream cleaning steps are applied. Validation
        includes:

        - Ensuring all required columns are present
        - Rejecting empty or whitespace only column names
        - Detecting pandas auto‑generated ``"Unnamed: X"`` columns when
          ``allow_unnamed`` is disabled

        Header validation is controlled by the ``headers.enabled`` flag in the
        configuration. When disabled, the DataFrame is returned unchanged.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame whose column headers will be validated.

        Returns
        -------
        DataFrame
            The original DataFrame if validation succeeds.

        Raises
        ------
        ValueError
            If required columns are missing, if any header is empty or
            whitespace only, or if unnamed columns are present when they are not
            allowed.

        Notes
        -----
        Pandas generates ``"Unnamed: X"`` headers when a CSV contains missing
        column names. These are treated as invalid unless explicitly permitted
        via ``allow_unnamed``.
        """
        logger.debug("Validating column headers")

        header_cfg = self.config.get("headers", {})
        if not header_cfg.get("enabled", False):
            return df

        required = header_cfg.get("required", [])
        allow_unnamed = header_cfg.get("allow_unnamed", False)

        # Detect missing required columns
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Detect empty or whitespace only headers
        bad_headers = [col for col in df.columns if col is None or str(col).strip() == ""]
        if bad_headers:
            raise ValueError(f"Invalid empty headers: {bad_headers}")

        # Detect pandas auto-generated "Unnamed: X" headers
        if not allow_unnamed:
            unnamed = [col for col in df.columns if str(col).startswith("Unnamed:")]
            if unnamed:
                raise ValueError(f"Unnamed headers detected: {unnamed}")

        logger.debug("Column header validation completed")
        return df

    def _drop_extra_columns(self, df):
        """
        Drop columns that are not part of the configured schema.

        This method enforces a strict column schema when enabled. If
        ``schema.drop_extra`` is set to ``True``, the DataFrame is reduced to
        only the columns listed in ``schema.required``. Columns not included in
        the required set are removed.

        Schema enforcement is controlled by the ``schema.enabled`` flag. When
        disabled, the DataFrame is returned unchanged.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame whose columns may be filtered based on the schema.

        Returns
        -------
        DataFrame
            A DataFrame containing only the required columns when
            ``drop_extra`` is enabled; otherwise the original DataFrame.

        Notes
        -----
        This operation does not validate missing required columns. Header
        validation should be performed separately via ``_validate_headers``.
        """
        logger.debug("Dropping extra columns")

        schema_cfg = self.config.get("schema", {})
        if not schema_cfg.get("enabled", False):
            return df

        required = set(schema_cfg.get("required", []))
        drop_extra = schema_cfg.get("drop_extra", False)

        if drop_extra:
            df = df[[col for col in df.columns if col in required]]

        logger.debug("Extra column removal completed")
        return df

    def _trim_strings(self, df):
        """
        Trim leading and trailing whitespace from configured string columns.

        This method applies whitespace trimming only to the columns explicitly
        listed in the ``trim_strings.columns`` configuration. Each targeted
        column is coerced to string and stripped of leading and trailing
        whitespace. No other transformations are performed.

        Trimming is controlled by the ``trim_strings.enabled`` flag. When
        disabled—or when the column list is empty—the DataFrame is returned
        unchanged.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame whose specified string columns may be trimmed.

        Returns
        -------
        DataFrame
            A copy of the input DataFrame with trimmed string columns when
            trimming is enabled; otherwise the original DataFrame.

        Notes
        -----
        Columns not listed in ``trim_strings.columns`` are never modified.
        This function does not collapse internal whitespace or change data
        types beyond coercing trimmed columns to string.
        """
        logger.debug("Trimming leading and trailing whitespaces")

        trim_strings_cfg = self.config.get("trim_strings", {})
        if not trim_strings_cfg.get("enabled", False):
            return df

        cols = trim_strings_cfg.get("columns", [])
        if not cols:
            return df

        df_copy = df.copy()
        for col in cols:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].astype(str).str.strip()

        logger.debug("Whitespace trimming completed")
        return df_copy

    def _remove_empty_rows(self, df):
        """
        Remove empty or whitespace only rows according to the configured rules.

        This method identifies and removes rows that contain no meaningful data.
        The process consists of two optional steps, each controlled by the
        ``empty_rows`` configuration:

        - Converting whitespace only cells to ``NaN`` when
          ``drop_whitespace_only`` is enabled
        - Dropping rows where all values are ``NaN`` when ``drop_all_nan`` is
          enabled

        Empty‑row removal is enabled by default unless explicitly disabled via
        ``empty_rows.enabled``.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame from which empty rows may be removed.

        Returns
        -------
        DataFrame
            A DataFrame with whitespace only cells normalized to ``NaN`` and
            all‑NaN rows removed, depending on configuration settings.

        Notes
        -----
        Converting whitespace only values to ``NaN`` ensures consistent behavior
        across CSVs that may contain visually empty but non‑null string fields.
        This step should occur early in the cleaning pipeline to avoid false
        validation failures in numeric or date checks.
        """
        logger.debug("Removing empty or whitespace only rows")

        empty_rows_cfg = self.config.get("empty_rows", {})
        if not empty_rows_cfg.get("enabled", True):
            return df

        # Convert whitespace to NaN (Not a Number)
        if empty_rows_cfg.get("drop_whitespace_only", True):
            df = df.replace(r'^\s*$', pd.NA, regex=True)

        # Drop rows where all values are NaN (Not a Number)
        if empty_rows_cfg.get("drop_all_nan", True):
            df = df.dropna(how="all")

        logger.debug("Removal of empty or whitespace only rows completed")
        return df

    def _fill_missing_values(self, df):
        """
        Fill missing values in configured columns using specified strategies.

        This method applies per‑column missing‑value strategies defined in the
        ``fill_missing_values.columns`` configuration. Only columns explicitly
        listed in the configuration are processed, and only when they contain
        missing values. Supported strategies include:

        - ``"mean"``: fill with the column's mean
        - ``"median"``: fill with the column's median
        - Any other value: treated as a literal fill value

        Missing‑value handling is controlled by the ``fill_missing_values.enabled``
        flag. When disabled—or when the DataFrame contains no missing values—the
        original DataFrame is returned unchanged.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame whose missing values may be filled.

        Returns
        -------
        DataFrame
            A copy of the input DataFrame with missing values filled according
            to the configured per‑column strategies.

        Notes
        -----
        - Columns not listed in ``fill_missing_values.columns`` are never modified.
        - Literal fill values allow flexible handling of categorical or string
          fields without requiring type inference.
        - Mean and median strategies assume the column is numeric; callers should
          ensure type validation occurs earlier in the pipeline.
        """
        logger.debug("Filling missing column values")

        if not df.isna().any().any():
            return df

        missing_values_cfg = self.config.get("fill_missing_values", {})
        if not missing_values_cfg.get("enabled", False):
            return df

        df_copy = df.copy()
        cols = missing_values_cfg.get("columns", {})

        for col, method in cols.items():
            if col not in df_copy.columns:
                continue

            series = df_copy[col]

            if series.isna().any():
                if method == "mean":
                    df_copy[col] = series.fillna(series.mean())
                elif method == "median":
                    df_copy[col] = series.fillna(series.median())
                else:
                    df_copy[col] = series.fillna(method)

        logger.debug("Filling missing column values completed")
        return df_copy

    def _fix_data_types(self, df):
        """
        Enforce configured data types on selected columns.

        This method applies explicit dtype conversions based on the
        ``dtypes.columns`` configuration. Only columns listed in the
        configuration are processed, and conversions are performed *only when
        the current dtype does not already match the target*. Supported target
        types include:

        - ``"int"``: coerced to numeric and stored as nullable ``Int64``
        - ``"float"``: coerced to numeric and stored as ``float64``
        - ``"bool"``: coerced using ``astype("bool")``
        - ``"string"``: coerced to pandas' ``string`` dtype
        - ``"datetime"``: parsed with ``pd.to_datetime`` and stored as
          ``datetime64[ns]``

        All conversions are applied with safe coercion semantics. Invalid values
        become ``NaN`` (or ``NaT`` for datetime) rather than raising exceptions.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame whose column types may be enforced.

        Returns
        -------
        DataFrame
            A copy of the input DataFrame with updated dtypes for configured
            columns.

        Notes
        -----
        - Nullable integer dtype (``Int64``) is used for integer columns to
          preserve missing values.
        - Datetime conversion is skipped when the column is already any
          ``datetime64`` dtype.
        - Numeric coercion uses ``errors="coerce"``, ensuring that malformed
          values do not interrupt the cleaning pipeline.
        """
        logger.debug("Enforcing configured data types")

        dtypes_cfg = self.config.get("dtypes", {})
        df_copy = df.copy()
        cols = dtypes_cfg.get("columns", {})

        for col, dtype in cols.items():
            if col not in df_copy.columns:
                continue

            # Only enforce dtype if needed
            current = df_copy[col].dtype

            if dtype == "int":
                if current != "int64" and current != "Int64":
                    df_copy[col] = pd.to_numeric(df_copy[col], errors="coerce").astype("Int64")
            elif dtype == "float":
                if current != "float64":
                    df_copy[col] = pd.to_numeric(df_copy[col], errors="coerce").astype("float64")
            elif dtype == "bool":
                if current != "bool":
                    df_copy[col] = df_copy[col].astype("bool")
            elif dtype == "string":
                if current != "object" and current != "string":
                    df_copy[col] = df_copy[col].astype("string")
            elif dtype == "datetime":
                # Only convert if not already datetime
                if not pd.api.types.is_datetime64_any_dtype(current):
                    df_copy[col] = pd.to_datetime(df_copy[col], errors="coerce")
                    df_copy[col] = df_copy[col].astype("datetime64[ns]")

        logger.debug("Data type enforcement completed")
        return df_copy

    def _validate_numeric(self, df):
        """
        Validate that configured columns contain only numeric values.

        This method performs strict numeric validation on the columns listed in
        the ``numeric.columns`` configuration. Each column is parsed using
        ``pd.to_numeric`` with ``errors="raise"``, ensuring that any non‑numeric
        value—such as alphabetic strings, mixed types, or malformed numbers—
        triggers an immediate failure.

        Numeric validation is controlled by the ``numeric.enabled`` flag. When
        disabled, no validation is performed.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame whose numeric columns will be validated.

        Returns
        -------
        None
            The method returns ``None`` on success. It raises an exception if
            any configured column contains invalid numeric data.

        Raises
        ------
        ValueError
            If any column listed in ``numeric.columns`` contains non‑numeric
            values.

        Notes
        -----
        - Validation occurs *before* any type coercion or missing‑value filling
          to ensure that malformed numeric fields are surfaced early.
        - ``pd.to_numeric(..., errors="raise")`` guarantees strict enforcement
          and prevents silent coercion to ``NaN``.
        """
        logger.debug("Validating configured numeric columns")

        numeric_cfg = self.config.get("numeric", {})
        if not numeric_cfg.get("enabled", False):
            return

        for col in numeric_cfg.get("columns", []):
            try:
                pd.to_numeric(df[col], errors="raise")
            except Exception:
                raise ValueError(f"Invalid numeric values in column '{col}'")

        logger.debug("Numeric column validating completed")

    def _validate_dates(self, df):
        """
        Validate date columns according to the configured date rules.

        This method parses and validates the columns listed in
        ``dates.columns`` using an optional explicit date format. Each column is
        converted with ``pd.to_datetime`` using ``errors="coerce"``, ensuring
        that malformed or non‑parseable values become ``NaT``. When strict mode
        is enabled, any ``NaT`` values are treated as validation failures.

        Date validation is controlled by the ``dates.enabled`` flag. When
        disabled, the DataFrame is returned unchanged.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame whose date columns will be validated.

        Returns
        -------
        DataFrame
            The original DataFrame if validation succeeds.

        Raises
        ------
        ValueError
            If strict mode is enabled and any configured date column contains
            invalid or unparseable date values.

        Notes
        -----
        - The optional ``dates.format`` setting allows enforcing a specific
          date pattern (e.g., ``"%Y-%m-%d"``). Values not matching the format
          become ``NaT``.
        - Strict mode ensures early detection of malformed dates before any
          downstream transformations occur.
        - Non‑strict mode allows ``NaT`` values to remain in the DataFrame,
          enabling later filling or type coercion.
        """
        logger.debug("Validating date columns")

        dates_cfg = self.config.get("dates", {})
        if not dates_cfg.get("enabled", False):
            return df

        fmt = dates_cfg.get("format")
        strict = dates_cfg.get("strict", False)

        for col in dates_cfg.get("columns", []):
            parsed = pd.to_datetime(df[col], format=fmt, errors="coerce")

            if strict and parsed.isna().any():
                bad = df.loc[parsed.isna(), col].tolist()
                raise ValueError(f"Invalid dates found in column '{col}': {bad}")

        logger.debug("Date column validating completed")
        return df

    def _remove_duplicates(self, df: DataFrame) -> DataFrame:
        """
        Remove duplicate rows according to the configured duplicate‑removal rules.

        This method identifies and removes duplicate rows using the settings in
        ``remove_duplicates``. It supports subset‑based duplicate detection,
        optional case‑insensitive comparison, and configurable strategies for
        determining which duplicate entries to retain. The supported ``keep``
        modes are:

        - ``"first"``: keep the first occurrence of each duplicate group
        - ``"last"``: keep the last occurrence
        - ``"none"``: drop *all* rows that participate in any duplicate group

        When case‑insensitive mode is enabled, all columns listed in the subset
        are lowercased prior to duplicate detection.

        Duplicate removal is controlled by the ``remove_duplicates.enabled`` flag.
        When disabled, the DataFrame is returned unchanged.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame from which duplicate rows may be removed.

        Returns
        -------
        DataFrame
            A copy of the input DataFrame with duplicates removed according to
            the configured rules.

        Raises
        ------
        ValueError
            If duplicate removal fails due to invalid configuration or unexpected
            data issues. Errors are logged before being raised.

        Notes
        -----
        - Case‑insensitive comparison applies only to columns listed in the
          ``subset`` configuration.
        - ``keep="none"`` removes *all* duplicates, not just additional copies.
        - The method always operates on a copy of the DataFrame to avoid
          mutating the caller's data.
        """
        logger.debug("Removing duplicate rows")

        remove_duplicates_cfg = self.config.get("remove_duplicates", {})
        if not remove_duplicates_cfg.get("enabled", True):
            logger.debug("Duplicate removal disabled")
            return df

        subset = remove_duplicates_cfg.get("subset")
        keep = remove_duplicates_cfg.get("keep", "first")
        case_insensitive = remove_duplicates_cfg.get("case_insensitive", False)

        df_copy = df.copy()

        try:
            if case_insensitive and subset:
                for col in subset:
                    if col in df_copy.columns:
                        df_copy[col] = (
                            df_copy[col]
                            .astype("string")
                            .str.lower()
                        )

            if keep == "none":
                mask = df_copy.duplicated(subset=subset, keep=False)
                df_copy = df_copy[~mask]
            else:
                df_copy = df_copy.drop_duplicates(
                    subset=subset,
                    keep=keep,
                )

        except Exception:
            logger.error("Duplicate removal failed", exc_info=True)
            raise

        logger.debug("Duplicate row removal completed")
        return df_copy

    def _apply_row_filters(self, df: DataFrame) -> DataFrame:
        """
        Apply row‑level filtering rules according to the configured filter set.

        This method evaluates a series of row‑level predicates defined in the
        ``row_filters`` configuration. Filters are applied sequentially and
        deterministically, with each step reducing the DataFrame based on the
        configured criteria. Supported filter types include:

        - **Required columns**: drop rows where specified columns contain ``NaN``
        - **Drop‑if‑equals rules**: remove rows where a column matches any value
          in a configured list
        - **Numeric ranges**: enforce minimum and/or maximum numeric bounds
        - **Regex matching**: retain rows whose string values match a pattern
        - **Keep‑if rules**: retain rows only when column values appear in a
          configured whitelist

        Row filtering is controlled by the ``row_filters.enabled`` flag. When
        disabled, the DataFrame is returned unchanged.

        Parameters
        ----------
        df : DataFrame
            Input DataFrame to be filtered.

        Returns
        -------
        DataFrame
            A copy of the input DataFrame after applying all configured
            row‑level filters.

        Raises
        ------
        ValueError
            If any filtering step fails due to invalid configuration or
            unexpected data issues. Errors are logged before being raised.

        Notes
        -----
        - Filters are applied in a fixed order: required columns → drop‑equals →
          numeric ranges → regex → keep‑if.
        - Regex matching uses ``str.match`` with ``na=False`` to ensure missing
          values do not pass the filter.
        - Numeric range filtering assumes the column contains comparable numeric
          values; callers should validate types earlier in the pipeline.
        - The method always operates on a copy of the DataFrame to avoid
          mutating the original input.
        """
        logger.debug("Applying row filters")

        row_filter_cfg = self.config.get("row_filters", {})
        if not row_filter_cfg.get("enabled", True):
            logger.debug("Row filtering disabled")
            return df

        df_copy = df.copy()

        try:
            # Required columns
            required = row_filter_cfg.get("required_columns", []) or []
            for col in required:
                if col in df_copy.columns:
                    df_copy = df_copy[df_copy[col].notna()]

            # Drop rows where column equals certain values
            drop_equals = row_filter_cfg.get("drop_if_equals", {}) or {}
            for col, values in drop_equals.items():
                if col in df_copy.columns:
                    df_copy = df_copy[~df_copy[col].isin(values)]

            # Numeric ranges
            ranges = row_filter_cfg.get("numeric_ranges", {}) or {}
            for col, rule in ranges.items():
                if col in df_copy.columns:
                    series = df_copy[col]
                    min_val = rule.get("min")
                    max_val = rule.get("max")

                    if min_val is not None:
                        df_copy = df_copy[series >= min_val]
                    if max_val is not None:
                        df_copy = df_copy[series <= max_val]

            # Regex matching
            regex_rules = row_filter_cfg.get("regex", {}) or {}
            for col, pattern in regex_rules.items():
                if col in df_copy.columns:
                    series = df_copy[col].astype("string")
                    df_copy = df_copy[
                        series.str.match(pattern, na=False)
                    ]

            # Keep-if rules
            keep_if = row_filter_cfg.get("keep_if", {}) or {}
            for col, values in keep_if.items():
                if col in df_copy.columns:
                    df_copy = df_copy[df_copy[col].isin(values)]

        except Exception:
            logger.error("Row filtering failed", exc_info=True)
            raise

        logger.debug("Row filtering completed")
        return df_copy
