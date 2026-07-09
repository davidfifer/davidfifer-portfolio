"""
Tests for validating the CSV Cleaner command‑line interface (CLI).

This module exercises the Typer‑based CLI defined in ``csv_cleaner.cli``.
It verifies correct behavior for help output, version reporting, the
``clean`` command (both valid and invalid CSVs), the ``profile`` command,
and direct module invocation. All tests use Typer's ``CliRunner`` to
simulate CLI calls without spawning subprocesses.
"""

import os
import tempfile

from csv_cleaner.cli import app
from typer.testing import CliRunner

runner = CliRunner()

TEST_DIR: str = os.path.dirname(__file__)
DATA_DIR = os.path.join(TEST_DIR, "data")


# ---------------------------------------------------------
# HELP COMMAND
# ---------------------------------------------------------
def test_cli_help():
    """
    Ensure the CLI displays help output and lists available commands.

    This test invokes ``--help`` and verifies that the CLI responds with
    usage information and includes the expected subcommands: ``clean``,
    ``profile``, and ``version``.
    """
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
    assert "clean" in result.stdout
    assert "profile" in result.stdout
    assert "version" in result.stdout


# ---------------------------------------------------------
# VERSION COMMAND
# ---------------------------------------------------------
def test_cli_version():
    """
    Ensure the CLI reports its version information.

    This test invokes the ``version`` command and checks that the output
    contains a case‑insensitive reference to "csv cleaner".
    """
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "csv cleaner" in result.stdout.lower()


# ---------------------------------------------------------
# CLEAN COMMAND — VALID CSV
# ---------------------------------------------------------
def test_cli_clean_valid_csv():
    """
    Ensure the ``clean`` command successfully processes a valid CSV file.

    This test provides a valid CSV and a test‑local configuration file,
    writes the cleaned output to a temporary directory, and verifies that
    the resulting CSV exists and contains expected cleaned email values.
    """
    input_csv = os.path.join(DATA_DIR, "valid_baseline.csv")
    config_path = os.path.join(TEST_DIR, "config", "rules.yaml")

    with tempfile.TemporaryDirectory() as tmp:
        output_csv = os.path.join(tmp, "out.csv")

        result = runner.invoke(
            app,
            [
                "clean",
                input_csv,
                "--config",
                config_path,
                "--output",
                output_csv,
            ],
        )

        assert result.exit_code == 0
        assert os.path.exists(output_csv)

        with open(output_csv) as f:
            content = f.read()
            assert "test@example.com" in content
            assert "test2@example.com" in content
            assert "test3@example.com" in content


# ---------------------------------------------------------
# CLEAN COMMAND — INVALID CSV
# ---------------------------------------------------------
def test_cli_clean_invalid_csv():
    """
    Ensure the ``clean`` command fails when given an invalid CSV file.

    This test uses a CSV with missing headers and verifies that the CLI
    exits with a non‑zero status code, indicating failure.
    """
    input_csv = os.path.join(DATA_DIR, "missing_headers.csv")
    config_path = os.path.join(TEST_DIR, "config", "rules.yaml")

    result = runner.invoke(
        app,
        [
            "clean",
            input_csv,
            "--config",
            config_path,
            "--output",
            "ignored.csv",
        ],
    )

    assert result.exit_code != 0


# ---------------------------------------------------------
# PROFILE COMMAND
# ---------------------------------------------------------
def test_cli_profile_runs():
    """
    Ensure the ``profile`` command runs successfully.

    This test invokes ``profile`` on a valid CSV and verifies that the
    command completes without errors.
    """
    input_csv = os.path.join(DATA_DIR, "valid_baseline.csv")
    result = runner.invoke(app, ["profile", input_csv])
    assert result.exit_code == 0


# ---------------------------------------------------------
# MODULE INVOCATION (NO SUBPROCESS)
# ---------------------------------------------------------
def test_cli_module_invocation():
    """
    Ensure the CLI responds to ``--help`` when invoked directly.

    This simulates ``python -m csv_cleaner`` by invoking the Typer app
    directly and verifying that help output is displayed.
    """
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
