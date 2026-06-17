"""
Package initialization.

Exposes package metadata such as version, author, and description.
"""

from importlib.metadata import version, PackageNotFoundError

__all__ = ["__version__", "__author__", "__description__"]

try:
    __version__ = version("file_sorter")
except PackageNotFoundError:
    __version__ = "1.0.0"

__author__ = "David Fifer"
__description__ = "Sorts files by type or modified date."
