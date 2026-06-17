import os
import sys
import json
import pytest
import logging
import file_organizer

from datetime import datetime


# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------
@pytest.fixture
def supported_types():
    return {
        "images": [".jpg", ".png"],
        "docs": [".txt", ".md"],
    }


@pytest.fixture
def temp_files(tmp_path):
    """Create a temporary folder with sample files."""
    f1 = tmp_path / "a.jpg"
    f2 = tmp_path / "b.txt"
    f3 = tmp_path / "c.unsupported"

    f1.write_text("img")
    f2.write_text("doc")
    f3.write_text("???")

    return tmp_path


# ------------------------------------------------------------
# setup_logging
# ------------------------------------------------------------
def test_setup_logging_uses_basic_config_when_missing(tmp_path, monkeypatch):
    # Reset logging so basicConfig will actually run
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    fake_path = tmp_path / "missing.conf"
    monkeypatch.setattr(file_organizer, "logging", logging)

    file_organizer.setup_logging(str(fake_path))

    # Should fall back to basicConfig → INFO level
    assert logging.getLogger().level == logging.INFO


# ------------------------------------------------------------
# load_config
# ------------------------------------------------------------
def test_load_config_reads_json(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"supported_file_types": {"docs": [".txt"]}}))

    class FakeConfig:
        def __init__(self, path):
            self.path = path

        def load(self):
            return {"supported_file_types": {"docs": [".txt"]}}

    monkeypatch.setattr(file_organizer, "Config", FakeConfig)

    cfg = file_organizer.load_config(str(cfg_file))
    assert cfg["supported_file_types"]["docs"] == [".txt"]


# ------------------------------------------------------------
# _sort_files (extension mode)
# ------------------------------------------------------------
def test_sort_files_by_extension(temp_files, supported_types):
    file_organizer._sort_files(str(temp_files), "extension", supported_types)

    assert (temp_files / "images" / "a.jpg").exists()
    assert (temp_files / "docs" / "b.txt").exists()
    assert (temp_files / "c.unsupported").exists()  # untouched


# ------------------------------------------------------------
# _sort_files (date mode)
# ------------------------------------------------------------
def test_sort_files_by_date(temp_files, supported_types, monkeypatch):
    # Force a known modification time
    fixed_time = datetime(2024, 1, 1)
    ts = fixed_time.timestamp()

    for f in temp_files.iterdir():
        os.utime(f, (ts, ts))

    file_organizer._sort_files(str(temp_files), "date", supported_types)

    date_folder = temp_files / "2024-01-01"
    assert (date_folder / "a.jpg").exists()
    assert (date_folder / "b.txt").exists()


# ------------------------------------------------------------
# _sort_files: validate full supported_file_types set
# ------------------------------------------------------------
def test_sort_files_full_supported_types(tmp_path):
    supported_types = {
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
        "documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
        "archives": [".zip", ".tar"],
    }

    # Create files for every extension in every category
    created_files = []
    for category, extensions in supported_types.items():
        for ext in extensions:
            f = tmp_path / f"{category}_file{ext}"
            f.write_text("x")
            created_files.append((category, f))

    # Add unsupported file
    unsupported = tmp_path / "random.weird"
    unsupported.write_text("nope")

    # Run sort
    file_organizer._sort_files(str(tmp_path), "extension", supported_types)

    # Validate each supported file moved into correct folder
    for category, f in created_files:
        expected = tmp_path / category / f.name
        assert expected.exists(), f"{f} should be in {category}/"

    # Unsupported file should remain untouched
    assert (tmp_path / "random.weird").exists()


# ------------------------------------------------------------
# create_and_populate_directory
# ------------------------------------------------------------
def test_create_and_populate_directory_moves_file(tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dest"

    src.write_text("hello")

    result = file_organizer.create_and_populate_directory(str(dst), str(src), "src.txt")

    assert result is True
    assert (dst / "src.txt").exists()


def test_create_and_populate_directory_retries_when_locked(tmp_path, monkeypatch):
    src = tmp_path / "locked.txt"
    dst = tmp_path / "dest"
    src.write_text("locked")

    # Simulate locked file for first 2 attempts, then unlocked
    calls = {"count": 0}

    def fake_is_locked(path):
        calls["count"] += 1
        return calls["count"] < 3

    monkeypatch.setattr(file_organizer, "is_file_locked", fake_is_locked)

    result = file_organizer.create_and_populate_directory(str(dst), str(src), "locked.txt", retries=5, delay=0)

    assert result is True
    assert (dst / "locked.txt").exists()
    assert calls["count"] >= 3


# ------------------------------------------------------------
# is_file_locked
# ------------------------------------------------------------
def test_is_file_locked_missing_file():
    with pytest.raises(FileNotFoundError):
        file_organizer.is_file_locked("does_not_exist.txt")


def test_is_file_locked_unlocked_file(tmp_path):
    f = tmp_path / "free.txt"
    f.write_text("x")

    assert file_organizer.is_file_locked(str(f)) is False


# ------------------------------------------------------------
# sort_by_extension / sort_by_modified_date (dry-run)
# ------------------------------------------------------------
def test_sort_by_extension_dry_run(monkeypatch, temp_files, supported_types):
    called = {"ran": False}

    def fake_sort(path, mode, types):
        called["ran"] = True

    monkeypatch.setattr(file_organizer, "_sort_files", fake_sort)

    file_organizer.sort_by_extension(str(temp_files), supported_types, dry_run_mode=True)

    # In dry‑run mode, the wrapped function is never invoked and `None` is returned.
    assert called["ran"] is False


def test_sort_by_date_dry_run(monkeypatch, temp_files, supported_types):
    called = {"ran": False}

    def fake_sort(path, mode, types):
        called["ran"] = True

    monkeypatch.setattr(file_organizer, "_sort_files", fake_sort)

    file_organizer.sort_by_modified_date(str(temp_files), supported_types, dry_run_mode=True)

    # In dry‑run mode, the wrapped function is never invoked and `None` is returned.
    assert called["ran"] is False


# ------------------------------------------------------------
# CLI: get_command_line_arguments
# ------------------------------------------------------------
def test_cli_parses_arguments(monkeypatch, tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()

    test_args = ["prog", "--folder_path", str(folder), "--sort_mode", "extension"]
    monkeypatch.setattr(sys, "argv", test_args)

    args = file_organizer.get_command_line_arguments()

    assert args.folder_path == str(folder)
    assert args.sort_mode == "extension"


def test_cli_errors_on_missing_folder(monkeypatch):
    test_args = ["prog", "--folder_path", "missing", "--sort_mode", "extension"]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit):
        file_organizer.get_command_line_arguments()


# ------------------------------------------------------------
# main() dispatch logic
# ------------------------------------------------------------
def test_main_dispatch_extension(monkeypatch, tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()

    # Fake config
    monkeypatch.setattr(file_organizer, "load_config", lambda: {
        "supported_file_types": {"docs": [".txt"]},
        "dry_run_mode": False
    })

    # Fake CLI
    class Args:
        folder_path = str(folder)
        sort_mode = "extension"
        verbose = 0

    monkeypatch.setattr(file_organizer, "get_command_line_arguments", lambda: Args)

    called = {"ext": False}

    def fake_sort(path, types, dry):
        called["ext"] = True

    monkeypatch.setattr(file_organizer, "sort_by_extension", fake_sort)

    file_organizer.main()

    assert called["ext"] is True


def test_main_dispatch_invalid_mode(monkeypatch, tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()

    monkeypatch.setattr(file_organizer, "load_config", lambda: {
        "supported_file_types": {},
        "dry_run_mode": False
    })

    class Args:
        folder_path = str(folder)
        sort_mode = "invalid"
        verbose = 0

    monkeypatch.setattr(file_organizer, "get_command_line_arguments", lambda: Args)

    with pytest.raises(SystemExit):
        file_organizer.main()
