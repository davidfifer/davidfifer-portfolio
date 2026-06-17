import json
from pathlib import Path

class Config:
    """
    Loads and parses a JSON configuration file from a given filesystem path.

    This class provides a simple interface for reading JSON-based configuration
    files. It validates that the file exists and contains valid JSON before
    returning the parsed configuration as a Python dictionary.
    """
    def __init__(self, path: str):
        """
        Initialize the Config loader.

        Args:
            path (str): Path to the JSON configuration file.
        """
        self.path = Path(path)

    def load(self) -> dict:
        """
        Load and parse the JSON configuration file.

        Reads the file at the configured path, verifies that it exists, and
        attempts to decode it as JSON. If the file is missing or contains
        invalid JSON, a descriptive exception is raised.

        Returns:
            dict: Parsed JSON content as a Python dictionary.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If the file contains invalid JSON.
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found: {self.path}")

        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
