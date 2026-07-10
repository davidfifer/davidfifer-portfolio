# CSV Test Data Suite

A comprehensive dataset for validation, normalization, and error‑handling tests.

---

## Overview

This suite provides a complete, end‑to‑end collection of CSV test files designed to exercise every major rule defined in
the data‑cleaning configuration from column normalization and string trimming to strict numeric/date validation,
missing‑value strategies, schema enforcement, and row‑level filtering.

Each file isolates a specific class of input irregularities, allowing tests to precisely target behaviors such as
alias‑based column normalization, dtype coercion, default and column‑specific fill‑missing logic, strict date parsing,
header validation, and multi‑rule row filtering. Together, these datasets ensure full coverage across unit, integration,
and regression tests and serve as a reliable foundation for validating the entire cleaning pipeline as it evolves.

---

## Canonical Schema

- The following schema defines the expected structure for all valid datasets. All validation rules reference this
canonical definition.

    | Column      | Type    | Required | Notes                     |
    |-------------|---------|----------|---------------------------|
    | user_id     | integer | yes      | Unique per user           |
    | email       | string  | yes      | Must contain “@”          |
    | age         | integer | yes      | Range: 0–120              |
    | price       | decimal | yes      | USD                       |
    | signup_date | date    | yes      | ISO‑8601 format           |
    | is_active   | boolean | yes      | ``true`` / ``false``      |
    | status      | string  | yes      | ``active`` / ``inactive`` |
    | country     | string  | yes      | Lowercase ISO‑2           |
    | zip_code    | string  | yes      | Postal/ZIP code           |

---

## File Index

| File                                                         | Purpose                         | Key Behaviors Triggered                                             |
|--------------------------------------------------------------|---------------------------------|---------------------------------------------------------------------|
| [bad_numeric_values.csv](#bad_numeric_valuescsv)             | Numeric validation & corruption | Non‑numeric numeric fields, mixed type coercion                     |
| [duplicates.csv](#duplicatescsv)                             | Duplicate detection             | Exact row duplication, ID/email consistency                         |
| [empty_rows.csv](#empty_rowscsv)                             | Empty‑row handling              | Blank/whitespace rows, structural validation                        |
| [extra_columns.csv](#extra_columnscsv)                       | Extra‑column handling           | Row expansion, schema mismatch                                      |
| [fix_data_types.csv](#fix_data_typescsv)                     | 	Type‑coercion correction       | 	Integer/float/date/bool normalization, coercion consistency        |
| [invalid_dates.csv](#invalid_datescsv)                       | Date validation                 | Non‑parseable dates, coercion failures                              |
| [missing_headers.csv](#missing_headerscsv)                   | Header validation               | Missing required headers, positional inference                      |
| [missing_required_columns.csv](#missing_required_columnscsv) | Fully valid dataset             | Baseline validation, clean schema                                   |
| [missing_values.csv](#missing_valuescsv)                     | 	Missing‑value handling	        | Blank fields, default fills, column‑specific overrides, consistency |
| [normalize_columns.csv](#normalize_columnscsv)               | Column normalization            | Alias mapping, canonical column enforcement                         |
| [trim_strings.csv](#trim_stringscsv)                         | String trimming                 | Leading/trailing whitespace, internal spacing rules                 |
| [row_filters.csv](#row_filterscsv)                           | Missing‑value defaults          | Median/mode/ffill/empty/id‑forbid behaviors                         |
| [unnamed_headers.csv](#unnamed_headerscsv)                   | Column‑specific missing rules   | age→mean, signup_date→1970‑01‑01, status→Unknown                    |
| [valid_baseline.csv](#valid_baselinecsv)                     | Type enforcement                | int/float/datetime/bool coercion                                    |

---

## Usage

These datasets are intended for:

- Unit tests validating individual normalization rules
- Integration tests for ingestion pipelines
- Regression tests when schema or validation logic changes
- Benchmarking normalization performance

Typical usage:
- load_csv("tests/data/bad_numeric_values.csv")

---

## Test file details

### bad_numeric_values.csv

- This test file verifies that your data‑cleaning pipeline correctly handles invalid numeric fields. It ensures the
pipeline detects and rejects values that cannot be parsed as integers or decimals, while still processing valid rows
normally.

#### Scenarios Covered:

- Invalid integer parsing
- Invalid decimal parsing
- Selective failure behavior
- Row‑level error handling

#### Sample csv:

| user_id | email             | age              | price         | signup_date | is_active | status | country | zip_code |
|---------|-------------------|------------------|---------------|-------------|-----------|--------|---------|----------|
| 1       | test@example.com  | **NOT_A_NUMBER** | 10.5          | 2024‑01‑01  | true      | ok     | us      | 12345    |
| 2       | test2@example.com | 40               | **BAD_PRICE** | 2024‑01‑02  | false     | ok     | canada  | 54321    |

---

### duplicates.csv

- This test file checks whether your pipeline can identify and handle duplicate rows. It ensures the system detects
repeated records, removes or reports them according to your configuration, and preserves unique rows without
interference.

#### Scenarios Covered:

- Duplicate row detection
- Primary key uniqueness
- Row‑level deduplication behavior
- No false positives

#### Sample csv:

| user_id | email             | age | price | signup_date | is_active | status | country | zip_code |
|---------|-------------------|-----|-------|-------------|-----------|--------|---------|----------|
| 1       | test@example.com  | 30  | 10.5  | 2024‑01‑01  | true      | ok     | us      | 12345    |
| 1       | test@example.com  | 30  | 10.5  | 2024‑01‑01  | true      | ok     | us      | 12345    |
| 2       | test2@example.com | 40  | 20.5  | 2024‑01‑02  | false     | ok     | canada  | 54321    |

---

### empty_rows.csv

- This test file validates how your pipeline handles fully empty rows. It ensures blank records are detected and dropped
or reported, while surrounding valid rows continue to be processed correctly.

#### Scenarios Covered:

- Empty row detection
- Required column enforcement
- Row‑level drop behavior
- No interference with valid rows

#### Sample csv:

| user_id   | email             | age       | price     | signup_date | is_active | status    | country   | zip_code  |
|-----------|-------------------|-----------|-----------|-------------|-----------|-----------|-----------|-----------|
| 1         | test@example.com  | 30        | 10.5      | 2024‑01‑01  | true      | ok        | us        | 12345     |
| *(empty)* | *(empty)*         | *(empty)* | *(empty)* | *(empty)*   | *(empty)* | *(empty)* | *(empty)* | *(empty)* |
| 2         | test2@example.com | 40        | 20.5      | 2024‑01‑02  | false     | ok        | canada    | 54321     |

---

### extra_columns.csv

- The purpose of this test file is to verify that your data‑cleaning pipeline correctly handles unexpected columns that
are not part of the defined schema. It ensures the pipeline can detect, ignore, drop, or report extra fields without
affecting the processing of valid, expected columns.

#### Scenarios Covered:

- Unexpected column detection
- Schema enforcement
- Column filtering behavior
- No interference with valid data

#### Sample csv:

| user_id | email            | age | price | signup_date | is_active | status | country | zip_code | extra1 | extra2 |
|---------|------------------|-----|-------|-------------|-----------|--------|---------|----------|--------|--------|
| 1       | test@example.com | 30  | 10.5  | 2024‑01‑01  | true      | ok     | us      | 12345    | foo    | bar    |

---

### fix_data_types.csv

- This test file verifies that your data‑cleaning pipeline correctly handles numeric fields wrapped in quotes. It
ensures the pipeline can parse quoted integers, decimals, dates, and booleans as valid values, treating them the same
as unquoted numeric fields.

#### Scenarios Covered:

- Quoted numeric parsing
- Quoted boolean/date parsing
- Schema consistency
- Valid row processing

#### Sample csv:

| user_id | email             | age  | price  | signup_date  | is_active | status | country | zip_code |
|---------|-------------------|------|--------|--------------|-----------|--------|---------|----------|
| 1       | test@example.com  | "30" | "10.5" | "2024‑01‑01" | "true"    | ok     | us      | 12345    |
| 2       | test2@example.com | "40" | "20.5" | "2024‑01‑02" | "false"   | ok     | canada  | 54321    |

---

### invalid_dates.csv

- This test file verifies that the pipeline correctly handles invalid or non‑parseable date values. It ensures the
system rejects or reports malformed dates while continuing to validate rows with proper date formats.

#### Scenarios Covered:

- Date parsing
- Coercion handling
- Schema consistency
- Valid row processing

#### Sample csv:

| user_id | email             | age | price | signup_date    | is_active | status | country | zip_code |
|---------|-------------------|-----|-------|----------------|-----------|--------|---------|----------|
| 1       | test@example.com  | 30  | 10.5  | **NOT_A_DATE** | true      | ok     | us      | 12345    |
| 2       | test2@example.com | 40  | 20.5  | 2024‑01‑02     | false     | ok     | canada  | 54321    |

---

### missing_headers.csv

- This test file verifies that the pipeline correctly handles missing or blank column headers. It ensures the system
detects incomplete header definitions and applies header‑level validation before processing any rows.

#### Scenarios Covered:

- Header validation
- Schema enforcement
- Positional inference
- Valid row processing

#### Sample csv:

| user_id | email            | age | price | signup_date | is_active | status | country | zip_code |
|---------|------------------|-----|-------|-------------|-----------|--------|---------|----------|
| 1       | test@example.com | 30  | 10.5  | 2024‑01‑01  | true      | ok     | us      | 12345    |

---

### missing_required_columns.csv

- This test file verifies that the pipeline correctly handles rows missing required columns. It ensures the system
detects incomplete records and rejects or flags them when mandatory fields (such as zip_code) are absent.

#### Scenarios Covered:

- Required‑column validation
- Schema enforcement
- Row‑level rejection
- Valid row processing

#### Sample csv:

| user_id | email            | age | price | signup_date  | is_active | status | country |
|---------|------------------|-----|-------|--------------|-----------|--------|---------|
| 1       | test@example.com | 30  | 10.5  | **1/1/2024** | TRUE      | ok     | us      |

---

### missing_values.csv

- This test file verifies that the pipeline correctly handles missing values across multiple columns. It ensures the
system applies default fill rules, column‑specific overrides, or row‑level rejection depending on your configuration.

#### Scenarios Covered:

- Missing‑value detection
- Default fill rules
- Column‑specific overrides
- Schema enforcement
- Valid row processing

#### Sample csv:

| user_id | email             | age         | price       | signup_date | is_active | status      | country |
|---------|-------------------|-------------|-------------|-------------|-----------|-------------|---------|
| 1       | test@example.com  | *(missing)* | 10.5        | 2024‑01‑01  | true      | ok          | us      | 12345 |
| 2       | test2@example.com | 40          | *(missing)* | *(missing)* | false     | *(missing)* | canada  | 54321 |
| 3       | test3@example.com | *(missing)* | 20.5        | 2024‑01‑03  | true      | ok          | us      | *(missing)* |

---

### normalize_columns.csv

- This test file verifies that the pipeline correctly performs column normalization, converting messy, inconsistent, or
incorrectly formatted headers into their canonical schema names.

#### Scenarios Covered:

- Header normalization
- Alias mapping
- Case and spacing cleanup
- Schema enforcement
- Valid row processing

#### Sample csv:

| emailaddress | zip              | age | price | signup_date | is_active | status | country | user_id |
|--------------|------------------|-----|-------|-------------|-----------|--------|---------|---------|
| 1            | TEST@EXAMPLE.COM | 30  | 10.5  | 2024‑01‑01  | true      | ok     | us      | 12345   |

---

### row_filters.csv

- This test file verifies that the pipeline correctly applies row‑level filtering rules, including regex validation,
numeric ranges, drop‑if conditions, and keep‑if conditions. It ensures only rows meeting all configured filter criteria
survive.

#### Scenarios Covered:

- Regex validation
- Numeric range filtering
- drop_if rules
- keep_if rules
- Schema enforcement
- Valid row processing

#### Sample csv:

| email | zip_code               | age         | price       | signup_date | is_active   | status      | country     | user_id     |
|-------|------------------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| 1     | alice@example.com      | 25          | 10.5        | 2024‑01‑01  | true        | active      | us          | 12345       |
| 2     | bob@example.com        | *(missing)* | 20.0        | 2024‑01‑02  | false       | inactive    | us          | 54321       |
| 3     | charlie_at_example.com | 17          | 5.0         | 2024‑01‑03  | true        | active      | ca          | 11111       |
| 4     | david@example.com      | 40          | 200.0       | 2024‑01‑04  | true        | banned      | us          | 22222       |
| 5     | eve@example.com        | 30          | 12.0        | 2024‑01‑05  | true        | active      | us          | 33333       |
| 6     | frank@example.com      | 55          | 77.0        | 2024‑01‑06  | true        | active      | uk          | 44444       |
| 7     | grace@example          | 22          | 65.0        | 2024‑01‑07  | true        | active      | us          | 55555       |
| 8     | heidi@example.com      | 19          | 5.0         | 2024‑01‑08  | true        | active      | us          | 66666       |
| 9     | ivan@example.com       | 70          | 150.0       | 2024‑01‑09  | true        | active      | us          | 77777       |
| 10    | judy@example.com       | 33          | 33.0        | 2024‑01‑10  | true        | pending     | us          | 88888       |
| 11    | karl@example.com       | 28          | 0.0         | 2024‑01‑11  | true        | active      | us          | 99999       |
| 12    | liam@example.com       | 45          | *(missing)* | *(missing)* | *(missing)* | *(missing)* | *(missing)* | *(missing)* |

---

### trim_strings.csv

- This test file verifies that the pipeline correctly performs string trimming, ensuring leading and trailing whitespace
is removed from string fields without altering internal spacing or valid content.

#### Scenarios Covered:

- Whitespace trimming
- Canonical normalization
- Schema enforcement
- Valid row processing

#### Sample csv:

| email | zip_code         | age | price | signup_date | is_active | status | country | user_id |
|-------|------------------|-----|-------|-------------|-----------|--------|---------|---------|
| 1     | test@example.com | 30  | 10.5  | 2024‑01‑01  | true      | ok     | us      | 12345   |

---

### unnamed_headers.csv

- This test file verifies that the pipeline correctly handles unnamed or placeholder headers. It ensures the system
detects incomplete or auto‑generated header names and applies header‑level validation before processing any rows.

#### Scenarios Covered:

- Header validation
- Missing/placeholder header detection
- Schema enforcement
- Positional inference
- Valid row processing

#### Sample csv:

| unnamed header | email            | age | price | signup_date | is_active | status | country | zip_code |
|----------------|------------------|-----|-------|-------------|-----------|--------|---------|----------|
| 1              | test@example.com | 30  | 10.5  | 2024‑01‑01  | true      | ok     | us      | 12345    |

---

### valid_baseline.csv

- This test file provides a clean, fully valid baseline dataset. It ensures the pipeline correctly processes rows that
already meet all schema, type, and formatting requirements without triggering normalization, coercion, or error
handling.

#### Scenarios Covered:

- Schema compliance
- Type correctness
- No missing values
- No normalization required
- Valid row processing

#### Sample csv:

| email | zip_code          | age | price | signup_date | is_active | status | country | user_id |
|-------|-------------------|-----|-------|-------------|-----------|--------|---------|---------|
| 1     | test@example.com  | 30  | 10.5  | 2024‑01‑01  | true      | ok     | us      | 12345   |
| 2     | test2@example.com | 40  | 20.5  | 2024‑01‑02  | false     | ok     | canada  | 54321   |
| 3     | test3@example.com | 25  | 15.5  | 2024‑01‑03  | true      | ok     | us      | 67890   |

---

## Summary

The test files in this suite provide complete coverage of all validation, normalization, and error‑handling scenarios
defined in the project’s configuration, including:

- Numeric corruption and strict numeric validation
- Duplicate‑row detection
- Empty‑row cleanup
- Extra‑column normalization
- Invalid and non‑ISO date handling
- Missing‑header and unnamed‑header detection
- Required‑column enforcement
- Column normalization via alias mapping
- String trimming and whitespace cleanup
- Missing‑value defaults and column‑specific overrides
- Type coercion for quoted values
- Schema enforcement and canonical structure validation
- Row‑level filtering rules (regex, ranges, drop_if, keep_if)
- Fully valid baseline rows for control‑case testing

This suite is fully aligned with the YAML configuration and provides comprehensive coverage for unit, integration, and
regression testing across the entire data‑cleaning pipeline.
