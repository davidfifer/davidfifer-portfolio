import os
import sys
import time
import shutil
import argparse
import logging
import logging.config
from datetime import datetime

from utils.config import Config
from utils.dry_run_decorator import dry_run

# Cross‑platform imports
if os.name == "nt":
    import msvcrt
else:
    import fcntl


def setup_logging(config_path=None):
    """
    Configure application logging using a configuration file when available,
    falling back to a basic INFO‑level setup when no config file exists.

    This function attempts to load a logging configuration from a specified
    path. If no path is provided, it resolves the default location relative
    to the module directory. When the configuration file is present, it uses
    `logging.config.fileConfig` to apply the settings. If the file is missing,
    it initializes logging with a simple `basicConfig` at INFO level.

    Args:
        config_path (str | None): Optional path to a logging configuration
            file. If omitted, the function resolves a default path in the
            project's `config/` directory.

    Returns:
        None: This function configures global logging and does not return a
        value.

    Raises:
        None: Missing configuration files do not raise errors; the function
        gracefully falls back to a default logging setup.

    Examples:
        >>> setup_logging()
        >>> setup_logging("/etc/myapp/logging.conf")
    """
    if config_path is None:
        base = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base, "..", "config", "logging.conf")

    if os.path.exists(config_path):
        logging.config.fileConfig(config_path, disable_existing_loggers=False)
    else:
        logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def load_config(config_path=None):
    """
    Load the application's JSON configuration file and return it as a dictionary.

    If no path is provided, this function resolves the default configuration
    file location relative to the module directory. It then delegates parsing
    to the `Config` class, which validates the file's existence and JSON format
    before returning the parsed configuration.

    Args:
        config_path (str | None): Optional path to a JSON configuration file.
            When omitted, the function uses the project's default
            `config/config.json` path.

    Returns:
        dict: Parsed configuration data loaded from the JSON file.

    Raises:
        FileNotFoundError: If the resolved configuration file does not exist.
        ValueError: If the configuration file contains invalid JSON.

    Examples:
        >>> load_config()
        >>> load_config("/etc/myapp/config.json")
    """
    if config_path is None:
        base = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base, "..", "config", "config.json")

    return Config(config_path).load()


def _sort_files(folder_path, sort_mode, supported_types):
    """
    Sort files in a directory into subfolders based on extension or last
    modified date.

    This function scans the target directory, identifies each file’s extension,
    and attempts to match it to a category defined in `supported_types`. Files
    are then moved into subfolders named after either their category
    (`sort_mode='extension'`) or their last modified date in YYYY‑MM‑DD format
    (`sort_mode='date'`). Unsupported file types are logged as warnings.

    File movement is delegated to `create_and_populate_directory`, and any
    errors raised during the move are caught and logged without interrupting
    the overall sorting process.

    Args:
        folder_path (str): Path to the directory whose files should be sorted.
        sort_mode (str): Sorting strategy. Must be either 'extension' or 'date'.
        supported_types (dict[str, list[str]]): Mapping of category names to
            lists of file extensions (lowercase, including the dot).

    Returns:
        None: The function performs file system operations and logs results.

    Raises:
        None: All file‑movement errors are caught and logged.

    Notes:
        - Directory entries that are not files are ignored.
        - Extensions are matched case‑insensitively.
        - Files with no extension are treated as `"no_extension"`.
        - A summary log entry is emitted after sorting completes.

    Examples:
        >>> _sort_files("/tmp/downloads", "extension", {"images": [".png", ".jpg"]})
        >>> _sort_files("/tmp/data", "date", {"docs": [".txt", ".md"]})
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if not os.path.isfile(file_path):
            continue

        ext = os.path.splitext(filename)[1].lower() or "no_extension"
        matched_category = None

        # Sort files into subfolders based on their file extension
        for category, extensions in supported_types.items():
            if ext in extensions:
                matched_category = category
                break

        if matched_category:
            destination_folder = None
            if sort_mode == 'date':
                mod_time = os.path.getmtime(file_path)
                date_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d")
                destination_folder = os.path.join(folder_path, date_str)
            elif sort_mode == 'extension':
                destination_folder = os.path.join(folder_path, str(matched_category))

            # Try moving the file
            try:
                create_and_populate_directory(str(destination_folder), file_path, filename)
            except Exception as e:
                logger.error(f"Failed to move file '{filename}': {e}")
        else:
            logger.warning(f"Unsupported file type: {ext.lstrip('.')}")

    logger.info(f"Files sorted by {sort_mode}")


def sort_by_extension(folder_path, supported_types, dry_run_mode=False):
    """
    Sort files in a directory into subfolders based on their file extensions.

    This function wraps the internal `_sort_files` routine with a dry‑run
    decorator, allowing callers to preview file‑movement operations without
    modifying the filesystem. When dry‑run mode is disabled, files are moved
    into category‑named subfolders according to the extension mappings defined
    in `supported_types`.

    Args:
        folder_path (str): Path to the directory whose files should be sorted.
        supported_types (dict[str, list[str]]): Mapping of category names to
            lists of supported file extensions (lowercase, including the dot).
        dry_run_mode (bool): When True, the decorated function logs intended
            actions instead of performing file operations.

    Returns:
        None: The function delegates sorting to `_sort_files` and does not
        return a value.

    Notes:
        - The dry‑run decorator logs the action description
          (“Sorted files by their extension”).
        - Actual sorting behavior is implemented in `_sort_files`.
        - Unsupported extensions are logged as warnings.

    Examples:
        >>> sort_by_extension("/tmp/downloads", {"images": [".png", ".jpg"]})
        >>> sort_by_extension("/tmp/data", {"docs": [".txt"]}, dry_run_mode=True)
    """
    @dry_run("Sorted files by their extension", dry_run=dry_run_mode)
    def _run(path):
        _sort_files(path, "extension", supported_types)

    _run(folder_path)


def sort_by_modified_date(folder_path, supported_types, dry_run_mode=False):
    """
    Sort files in a directory into subfolders based on their last modified date.

    This function wraps the internal `_sort_files` routine with a dry‑run
    decorator, allowing callers to preview file‑movement operations without
    modifying the filesystem. When dry‑run mode is disabled, files are moved
    into subfolders named after their modification date in `YYYY‑MM‑DD` format.
    Extension categories are still required to determine which files are eligible
    for sorting.

    Args:
        folder_path (str): Path to the directory whose files should be sorted.
        supported_types (dict[str, list[str]]): Mapping of category names to
            lists of supported file extensions (lowercase, including the dot).
        dry_run_mode (bool): When True, the decorated function logs intended
            actions instead of performing file operations.

    Returns:
        None: The function delegates sorting to `_sort_files` and does not
        return a value.

    Notes:
        - The dry‑run decorator logs the action description
          (“Sorted files by their modified date”).
        - Actual sorting behavior is implemented in `_sort_files`.
        - Unsupported extensions are logged as warnings.
        - Only files (not directories) are processed.

    Examples:
        >>> sort_by_modified_date("/tmp/downloads", {"docs": [".txt", ".md"]})
        >>> sort_by_modified_date("/tmp/data", {"images": [".png"]}, dry_run_mode=True)
    """
    @dry_run("Sorted files by their modified date", dry_run=dry_run_mode)
    def _run(path):
        _sort_files(path, "date", supported_types)

    _run(folder_path)


def create_and_populate_directory(folder_path, file_path, filename, retries=5, delay=1):
    """
    Move a file into a target directory, retrying when the file is locked.

    This function attempts to move `file_path` into `folder_path` under the
    specified `filename`. Before each attempt, it checks whether the file is
    locked using `is_file_locked`. If the file is locked, the function waits
    for `delay` seconds and retries, up to the configured number of `retries`.
    The destination directory is created if it does not already exist.

    Args:
        folder_path (str): Destination directory where the file should be moved.
        file_path (str | PathLike): Path to the file being moved.
        filename (str): Name to assign to the file inside the destination folder.
        retries (int): Number of retry attempts if the file is locked.
        delay (int | float): Seconds to wait between retry attempts.

    Returns:
        bool: True if the file was successfully moved; False if all attempts
        failed due to the file remaining locked.

    Notes:
        - Uses `is_file_locked` to determine lock status.
        - Logs a warning for each failed attempt and a final info message if
          the move ultimately fails.
        - File movement uses `shutil.move`, which overwrites existing files
          depending on platform behavior.

    Examples:
        >>> create_and_populate_directory("/tmp/archive", "/tmp/file.txt", "file.txt")
        True
    """
    for attempt in range(retries):
        if not is_file_locked(file_path):
            os.makedirs(folder_path, exist_ok=True)
            shutil.move(str(file_path), os.path.join(str(folder_path), filename))
            return True

        logger.warning(f"Attempt {attempt+1}: File is locked, retrying in {delay}s...")
        time.sleep(delay)

    logger.info(f"Failed to move '{filename}' after {retries} attempts (still locked).")
    return False


def is_file_locked(filepath):
    """
    Determine whether a file is currently locked by another process.

    This function attempts to open the file in append‑binary mode and acquire
    a non‑blocking exclusive lock. The implementation is platform‑specific:
    on Windows, it uses `msvcrt.locking`; on Unix‑like systems, it uses
    `fcntl.flock`. If the lock cannot be acquired, the file is considered
    locked. Permission errors are treated as lock failures and logged.

    Args:
        filepath (str | PathLike): Path to the file to test for a lock.

    Returns:
        bool: True if the file is locked or cannot be opened; False if the
        file is not locked and an exclusive lock can be acquired.

    Raises:
        FileNotFoundError: If the file does not exist at the provided path.

    Notes:
        - Lock detection is advisory on Unix‑like systems and mandatory on
          Windows.
        - Permission errors (e.g., insufficient rights) are logged and treated
          as lock conditions.
        - The file is opened in `'a+b'` mode to avoid modifying contents.

    Examples:
        >>> is_file_locked("/tmp/data.txt")
        False
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        with open(filepath, "a+b") as f:
            if os.name == "nt":
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                    return False
                except OSError:
                    return True
            else:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    return False
                except BlockingIOError:
                    return True
    except PermissionError:
        logger.error(f"Cannot open '{filepath}' due to permissions or lock")
        return True


def get_command_line_arguments():
    """
    Parse and validate command‑line arguments for the file‑sorting utility.

    This function configures an argument parser for three parameters:
    `--folder_path` (required), `--sort_mode` (required), and an optional
    verbosity flag (`-v` / `--verbose`). It validates that the provided folder
    path exists and is a directory. If validation fails, the function logs an
    error and terminates the program. On success, it returns the parsed
    arguments object.

    Returns:
        argparse.Namespace: Parsed command‑line arguments containing:
            - folder_path (str): Path to the directory to organize.
            - sort_mode (str): Sorting mode, either "extension" or "date".
            - verbose (int): Verbosity level (0, 1, 2, ...).

    Raises:
        SystemExit: If the folder path does not exist or is not a directory.
            `argparse` may also raise SystemExit for malformed input.

    Notes:
        - Verbosity increases with repeated `-v` flags.
        - A log entry is emitted when the folder path is accepted.

    Examples:
        >>> get_command_line_arguments()
    """
    parser = argparse.ArgumentParser(
        description="Command line arguments: --folder_path, --sort_mode, --verbose."
    )

    parser.add_argument(
        "--folder_path",
        type=str,
        required=True,
        help="Path to the directory you want to organize."
    )

    parser.add_argument(
        "--sort_mode",
        type=str,
        choices=["extension", "date"],
        required=True,
        help="Sorting mode: 'extension' or 'date'."
    )

    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (use -vv for more)."
    )

    args = parser.parse_args()

    # Validate folder path
    if not os.path.isdir(args.folder_path):
        logger.error(f"Error: The path '{args.folder_path}' does not exist or is not a directory.")
        sys.exit(1)

    logger.info(f"Processing path: {args.folder_path}")
    return args


def main():
    """
    Entry point for the file‑sorting utility.

    This function initializes logging, loads application configuration, parses
    command‑line arguments, and dispatches the appropriate sorting routine based
    on the selected mode. It supports optional dry‑run behavior (configured via
    the JSON config file) and dynamic verbosity control via the `-v` flag.

    The function validates the folder path through `get_command_line_arguments`
    and adjusts the logger level when verbose mode is enabled. It then invokes
    either `sort_by_extension` or `sort_by_modified_date` depending on the
    requested sorting strategy. Invalid sort modes result in an error log and
    program termination.

    Returns:
        None: This function orchestrates program flow and does not return a
        value.

    Raises:
        SystemExit: If an invalid sort mode is provided or if argument parsing
        fails (via `argparse`).

    Notes:
        - Logging configuration is loaded before any other operations.
        - Supported file types and dry‑run mode are read from the JSON config.
        - Verbosity increases with repeated `-v` flags.
        - Sorting functions handle their own logging and error reporting.

    Examples:
        >>> if __name__ == "__main__":
        ...     main()
    """
    setup_logging()
    cfg = load_config()

    args = get_command_line_arguments()
    folder_path = args.folder_path
    sort_mode = args.sort_mode
    supported_types = cfg["supported_file_types"]
    dry_run_mode = cfg.get("dry_run_mode", False)

    # If the verbose command line argument was passed in update the logger level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info(f"Setting logger level to verbose command line argument.")

    if sort_mode == "extension":
        sort_by_extension(folder_path, supported_types, dry_run_mode)
    elif sort_mode == "date":
        sort_by_modified_date(folder_path, supported_types, dry_run_mode)
    else:
        logger.error("Invalid sort mode. Use 'extension' or 'date'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
