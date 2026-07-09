"""
Configuration file loader for YAML and JSON formats.

This module provides the `ConfigLoader` class, which loads configuration
data from YAML (`.yaml`, `.yml`) or JSON (`.json`) files and returns the
parsed content as a Python dictionary. It includes format detection,
error logging, and dedicated loader methods for each supported format.
"""

import json
import yaml
import logging

from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Load YAML or JSON configuration files.

    Parameters
    ----------
    path : str
        Path to the configuration file. Supported formats are `.yaml`,
        `.yml`, and `.json`.

    Attributes
    ----------
    config_path : str
        The filesystem path to the configuration file.
    """

    def __init__(self, path: str) -> None:
        self.config_path = path

    def load(self) -> Dict[str, Any]:
        """
        Load a configuration file based on its extension.

        Determines whether `self.config_path` refers to a YAML or JSON file
        and dispatches to the appropriate loader method. Supported formats
        are `.yaml`, `.yml`, and `.json`. If the file extension does not
        match any supported type, an error is logged and a ValueError is
        raised.

        Returns
        -------
        dict
            Parsed configuration data.

        Raises
        ------
        ValueError
            If the file extension is not a supported YAML or JSON format.
        """
        logger.info("Loading configuration from %s", self.config_path)

        if self.config_path.endswith((".yaml", ".yml")):
            logger.debug("Detected YAML configuration format")
            return self._load_yaml()

        if self.config_path.endswith(".json"):
            logger.debug("Detected JSON configuration format")
            return self._load_json()

        logger.error(
            "Unsupported configuration file extension: %s",
            self.config_path
        )
        raise ValueError("Unsupported config format: ".format(self.config_path))

    def _load_yaml(self) -> Dict[str, Any]:
        """
        Load and parse a YAML configuration file.

        Opens the file located at `self.config_path` and deserializes its
        contents into a Python dictionary using `yaml.safe_load`.

        Returns
        -------
        dict
            Parsed YAML data loaded from the file.

        Raises
        ------
        FileNotFoundError
            If the file at `self.config_path` does not exist.
        yaml.YAMLError
            If the file contains invalid YAML syntax.
        OSError
            If the file cannot be opened or read.
        """
        logger.debug("Opening YAML file: %s", self.config_path)

        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                logger.debug("YAML configuration loaded successfully")
                return data
        except Exception:
            logger.error(
                "Failed to load YAML configuration from %s",
                self.config_path,
                exc_info=True
            )
            raise

    def _load_json(self) -> Dict[str, Any]:
        """
        Load and parse a JSON configuration file.

        Opens the file located at `self.config_path` and deserializes its
        contents into a Python dictionary using the standard JSON parser.

        Returns
        -------
        dict
            Parsed JSON data loaded from the file.

        Raises
        ------
        FileNotFoundError
            If the file at `self.config_path` does not exist.
        json.JSONDecodeError
            If the file contains invalid JSON.
        OSError
            If the file cannot be opened or read.
        """
        logger.debug("Opening JSON file: %s", self.config_path)

        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                logger.debug("JSON configuration loaded successfully")
                return data
        except Exception:
            logger.error(
                "Failed to load JSON configuration from %s",
                self.config_path,
                exc_info=True
            )
            raise
