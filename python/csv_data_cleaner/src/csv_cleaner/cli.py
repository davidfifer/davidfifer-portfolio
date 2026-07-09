"""
Typer-based command-line interface for the CSV Cleaner tool.

This module defines the CLI commands for cleaning, profiling, and inspecting
CSV files. It wires together the core components of the cleaning pipeline,
including the Cleaner, Profiler, and Exporter classes, and exposes them
through a user-friendly command-line interface built with Typer.
"""

import typer
import logging

from csv_cleaner.cleaner import Cleaner
from csv_cleaner.exporter import Exporter
from csv_cleaner.profiler import Profiler
from csv_cleaner.config_loader import ConfigLoader

logger = logging.getLogger(__name__)
app = typer.Typer(help="CSV Cleaner - cleanup and profile CSV files.")


@app.command()
def clean(
    show_profile: bool = typer.Option(False, "--show-profile", help="Display cleaning metrics."),
    file_path: str = typer.Argument(..., help="Path to the CSV file to clean."),
    config: str = typer.Option(..., "--config", "-c", help="Path to the config YAML/JSON file."),
    output: str = typer.Option(..., "--output", "-o", help="Path to save the cleaned CSV."),
) -> None:
    try:
        cfg = ConfigLoader(config).load()
        logger.debug("Configuration loaded successfully")

        cleaner = Cleaner(cfg)
        profiler = Profiler()
        exporter = Exporter()

        logger.info("Cleaning CSV file %s", file_path)
        df_clean = cleaner.clean(file_path)
        logger.debug("Cleaning completed; DataFrame shape: %s", getattr(df_clean, "shape", None))

        if show_profile:
            logger.info("Generating cleaning profile")
            metrics = profiler.profile(df_clean)
            typer.echo("Cleaning Profile:")
            typer.echo(metrics)

        logger.info("Saving cleaned CSV to %s", output)
        exporter.save(df_clean, output)

        typer.echo(f"Cleaned CSV saved to {output}")
        logger.info("Clean operation completed successfully")
    except Exception:
        logger.error("Clean operation failed", exc_info=True)
        raise typer.Exit(code=1)


@app.command()
def profile(
    file_path: str = typer.Argument(..., help="Path to the CSV file to profile.")
) -> None:
    logger.info("Starting profile operation")
    logger.debug("Arguments: file_path=%s", file_path)

    try:
        import pandas as pd

        logger.info("Reading CSV file %s", file_path)
        df = pd.read_csv(file_path)
        logger.debug("CSV loaded; DataFrame shape: %s", df.shape)

        profiler = Profiler()
        metrics = profiler.profile(df)

        typer.echo(metrics)
        logger.info("Profile operation completed successfully")
    except Exception:
        logger.error("Profile operation failed", exc_info=True)
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    logger.info("Displaying version information")
    typer.echo("CSV Cleaner v1.0.0")
