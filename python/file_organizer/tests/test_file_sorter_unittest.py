import os
import shutil
import tempfile
import unittest
import file_organizer

from datetime import datetime
from unittest.mock import patch, mock_open


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def make_file(path, name, content="x"):
    full = os.path.join(path, name)
    with open(full, "w") as f:
        f.write(content)
    return full


# ------------------------------------------------------------
# setup_logging
# ------------------------------------------------------------
class TestSetupLogging(unittest.TestCase):

    @patch("logging.config.fileConfig")
    @patch("os.path.exists", return_value=True)
    def test_setup_logging_with_config(self, mock_exists, mock_fileConfig):
        file_organizer.setup_logging("dummy.conf")
        mock_fileConfig.assert_called_once()

    @patch("logging.basicConfig")
    @patch("os.path.exists", return_value=False)
    def test_setup_logging_fallback(self, mock_exists, mock_basic):
        file_organizer.setup_logging("missing.conf")
        mock_basic.assert_called_once()


# ------------------------------------------------------------
# load_config
# ------------------------------------------------------------
class TestLoadConfig(unittest.TestCase):

    @patch("file_organizer.Config")
    def test_load_config(self, mock_cfg):
        instance = mock_cfg.return_value
        instance.load.return_value = {"x": 1}

        result = file_organizer.load_config("dummy.json")
        self.assertEqual(result, {"x": 1})
        instance.load.assert_called_once()


# ------------------------------------------------------------
# is_file_locked
# ------------------------------------------------------------
class TestIsFileLocked(unittest.TestCase):

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            file_organizer.is_file_locked("nope.txt")

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_unix_not_locked(self, mock_exists, mock_file):
        if os.name == "nt":
            self.skipTest("Windows lock behavior tested separately")

        with patch("fcntl.flock") as mock_flock:
            mock_flock.return_value = None
            self.assertFalse(file_organizer.is_file_locked("x.txt"))

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_unix_locked(self, mock_exists, mock_file):
        if os.name == "nt":
            self.skipTest("Windows lock behavior tested separately")

        with patch("fcntl.flock", side_effect=BlockingIOError):
            self.assertTrue(file_organizer.is_file_locked("x.txt"))

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", side_effect=PermissionError)
    def test_permission_error(self, mock_open, mock_exists):
        self.assertTrue(file_organizer.is_file_locked("x.txt"))


# ------------------------------------------------------------
# create_and_populate_directory
# ------------------------------------------------------------
class TestCreateAndPopulateDirectory(unittest.TestCase):

    @patch("file_organizer.is_file_locked", return_value=False)
    @patch("shutil.move")
    @patch("os.makedirs")
    def test_successful_move(self, mock_mkdir, mock_move, mock_locked):
        result = file_organizer.create_and_populate_directory(
            "dest", "file.txt", "file.txt"
        )
        self.assertTrue(result)
        mock_move.assert_called_once()

    @patch("file_organizer.is_file_locked", return_value=True)
    @patch("time.sleep")
    def test_locked_all_retries(self, mock_sleep, mock_locked):
        result = file_organizer.create_and_populate_directory(
            "dest", "file.txt", "file.txt", retries=3, delay=0
        )
        self.assertFalse(result)
        self.assertEqual(mock_sleep.call_count, 3)


# ------------------------------------------------------------
# _sort_files
# ------------------------------------------------------------
class TestSortFilesInternal(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.mkdtemp()
        self.supported = {
            "images": [".jpg", ".png"],
            "docs": [".txt"]
        }

    def tearDown(self):
        shutil.rmtree(self.temp)

    @patch("file_organizer.create_and_populate_directory")
    def test_extension_sort(self, mock_move):
        make_file(self.temp, "a.jpg")
        make_file(self.temp, "b.txt")

        file_organizer._sort_files(self.temp, "extension", self.supported)

        calls = [c.args[0] for c in mock_move.call_args_list]
        self.assertIn(os.path.join(self.temp, "images"), calls)
        self.assertIn(os.path.join(self.temp, "docs"), calls)

    @patch("file_organizer.create_and_populate_directory")
    def test_date_sort(self, mock_move):
        f = make_file(self.temp, "a.jpg")
        ts = datetime(2024, 1, 1).timestamp()
        os.utime(f, (ts, ts))

        file_organizer._sort_files(self.temp, "date", self.supported)

        expected_folder = os.path.join(self.temp, "2024-01-01")
        self.assertEqual(mock_move.call_args[0][0], expected_folder)

    @patch("file_organizer.logger")
    def test_unsupported_type(self, mock_logger):
        make_file(self.temp, "a.exe")
        file_organizer._sort_files(self.temp, "extension", self.supported)
        mock_logger.warning.assert_called()


# ------------------------------------------------------------
# Full supported_file_types coverage test
# ------------------------------------------------------------
class TestAllSupportedFileTypes(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.mkdtemp()

        self.supported = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
            "documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
            "archives": [".zip", ".tar"],
        }

    def tearDown(self):
        shutil.rmtree(self.temp)

    @patch("file_organizer.create_and_populate_directory")
    def test_all_supported_extensions_are_sorted(self, mock_move):
        # Create one file for each supported extension
        for category, extensions in self.supported.items():
            for ext in extensions:
                make_file(self.temp, f"test_{category}{ext}")

        file_organizer._sort_files(self.temp, "extension", self.supported)

        # Collect all destination folders used
        called_destinations = {call.args[0] for call in mock_move.call_args_list}

        # Ensure each category folder was used at least once
        for category in self.supported.keys():
            expected_folder = os.path.join(self.temp, category)
            assert expected_folder in called_destinations, f"Missing folder: {category}"

        # Ensure number of moves equals number of created files
        total_files = sum(len(exts) for exts in self.supported.values())
        assert mock_move.call_count == total_files


# ------------------------------------------------------------
# sort_by_extension / sort_by_modified_date (dry-run wrapper)
# ------------------------------------------------------------
class TestPublicSortFunctions(unittest.TestCase):

    @patch("file_organizer._sort_files")
    def test_sort_by_extension(self, mock_sort):
        file_organizer.sort_by_extension("path", {"x": [".txt"]}, dry_run_mode=False)
        mock_sort.assert_called_once()

    @patch("file_organizer._sort_files")
    def test_sort_by_date(self, mock_sort):
        file_organizer.sort_by_modified_date("path", {"x": [".txt"]}, dry_run_mode=False)
        mock_sort.assert_called_once()


# ------------------------------------------------------------
# get_command_line_arguments
# ------------------------------------------------------------
class TestCLIArguments(unittest.TestCase):

    @patch("file_organizer.os.path.isdir", return_value=True)
    @patch("file_organizer.sys.argv", ["prog", "--folder_path", "/tmp", "--sort_mode", "extension"])
    def test_valid_args(self, mock_isdir):
        args = file_organizer.get_command_line_arguments()
        assert args.folder_path == "/tmp"
        assert args.sort_mode == "extension"

    @patch("file_organizer.os.path.isdir", return_value=False)
    @patch("file_organizer.sys.exit")
    @patch("file_organizer.sys.argv", ["prog", "--folder_path", "/tmp", "--sort_mode", "extension"])
    def test_invalid_path(self, mock_exit, mock_exists):
        file_organizer.get_command_line_arguments()
        mock_exit.assert_called_once()

    @patch("file_organizer.sys.argv", ["prog"])
    def test_missing_args(self):
        with self.assertRaises(SystemExit) as cm:
            file_organizer.get_command_line_arguments()

        # argparse uses exit code 2 for argument errors
        assert cm.exception.code == 2


# ------------------------------------------------------------
# main()
# ------------------------------------------------------------
class TestMain(unittest.TestCase):

    @patch("file_organizer.setup_logging")
    @patch("file_organizer.load_config", return_value={
        "supported_file_types": {"docs": [".txt"]},
        "dry_run_mode": False
    })
    @patch("file_organizer.get_command_line_arguments")
    @patch("file_organizer.sort_by_extension")
    def test_main_extension(self, mock_sort, mock_args, mock_cfg, mock_log):
        mock_args.return_value.folder_path = "/tmp"
        mock_args.return_value.sort_mode = "extension"
        mock_args.return_value.verbose = 0

        file_organizer.main()
        mock_sort.assert_called_once()

    @patch("file_organizer.setup_logging")
    @patch("file_organizer.load_config", return_value={
        "supported_file_types": {"docs": [".txt"]},
        "dry_run_mode": False
    })
    @patch("file_organizer.get_command_line_arguments")
    @patch("file_organizer.sort_by_modified_date")
    def test_main_date(self, mock_sort, mock_args, mock_cfg, mock_log):
        mock_args.return_value.folder_path = "/tmp"
        mock_args.return_value.sort_mode = "date"
        mock_args.return_value.verbose = 0

        file_organizer.main()
        mock_sort.assert_called_once()

    @patch("file_organizer.sys.exit")
    @patch("file_organizer.setup_logging")
    @patch("file_organizer.load_config", return_value={
        "supported_file_types": {"docs": [".txt"]},
        "dry_run_mode": False
    })
    @patch("file_organizer.get_command_line_arguments")
    def test_main_invalid_mode(self, mock_args, mock_cfg, mock_log, mock_exit):
        mock_args.return_value.folder_path = "/tmp"
        mock_args.return_value.sort_mode = "nope"
        mock_args.return_value.verbose = 0

        file_organizer.main()
        mock_exit.assert_called_once()
