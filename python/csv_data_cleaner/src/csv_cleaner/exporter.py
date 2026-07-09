"""
CSV export utilities for the CSV Cleaner application.

This module provides the `Exporter` class, responsible for writing cleaned
pandas DataFrames to disk. It includes validation, automatic directory
creation, and detailed error logging to ensure reliable and predictable
output behavior.
"""

import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class Exporter:
    """
    Export pandas DataFrames to CSV files with validation and error handling.

    The exporter ensures that the DataFrame is valid, creates parent
    directories when necessary, and logs detailed error information if
    writing fails.
    """

    def save(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Save a pandas DataFrame to a CSV file.

        This method validates the DataFrame, ensures the output directory
        exists, and writes the CSV file to disk. Errors during directory
        creation or file writing are logged and re-raised with descriptive
        messages.

        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame to write to disk. Must be a valid, non-empty DataFrame.
        output_path : str
            The file path where the CSV will be written. Parent directories are
            created automatically if they do not already exist.

        Raises
        ------
        ValueError
            If `df` is not a pandas DataFrame or if it is empty.
        OSError
            If the output directory cannot be created or if writing the CSV fails.
        """
        # Validate DataFrame
        if not isinstance(df, pd.DataFrame):
            logger.error(
                "Invalid input type: expected DataFrame, got %s",
                type(df).__name__,
            )
            raise ValueError("Input must be a pandas DataFrame.")

        if df.empty:
            logger.error("Cannot save empty DataFrame to %s", output_path)
            raise ValueError("Cannot save an empty DataFrame.")

        # Ensure directory exists
        directory = os.path.dirname(output_path)

        if directory:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.debug("Ensured directory exists: %s", directory)
            except OSError:
                logger.error(
                    "Failed to create directory %s",
                    directory,
                    exc_info=True,
                )
                raise

        # Write CSV
        try:
            logger.info("Writing CSV to %s", output_path)
            df.to_csv(output_path, index=False)
        except Exception:
            logger.error(
                "Failed to write CSV to %s",
                output_path,
                exc_info=True,
            )
            raise
