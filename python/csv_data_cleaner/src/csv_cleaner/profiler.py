"""
Lightweight DataFrame profiling utilities.

This module provides the `Profiler` class, which generates basic structural
and data‑quality metrics for pandas DataFrames. It is intended for quick,
human‑readable diagnostics rather than full statistical profiling.
"""

import logging
import pandas as pd

from typing import Dict, Any

logger = logging.getLogger(__name__)


class Profiler:
    """
    Generate lightweight profiling metrics for pandas DataFrames.

    The profiler computes simple structural insights such as row counts,
    missing‑value distribution, and column data types. It is designed to
    support fast feedback during CSV cleaning workflows.
    """

    def profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute basic profiling metrics for a DataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame to analyze.

        Returns
        -------
        dict
            A dictionary containing:
            - "row_count": Total number of rows.
            - "missing_values": Mapping of column names to missing‑value counts.
            - "dtypes": Mapping of column names to their stringified data types.
        """
        logger.info("Starting DataFrame profiling")

        if not isinstance(df, pd.DataFrame):
            logger.error(
                "Invalid input type for profiling: expected DataFrame, got %s",
                type(df).__name__,
            )
            raise ValueError("Profiler requires a pandas DataFrame")

        logger.debug("Profiling DataFrame with shape: %s", df.shape)

        try:
            metrics = {
                "row_count": len(df),
                "missing_values": df.isna().sum().to_dict(),
                "dtypes": df.dtypes.astype(str).to_dict(),
            }

            logger.debug("Profiling completed successfully")
            return metrics
        except Exception:
            logger.error(
                "Unexpected error during profiling",
                exc_info=True)
            raise
