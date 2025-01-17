import os
import pytest
from unittest import mock
from unittest.mock import patch
from argparse import Namespace
from refcheck.settings import Settings
from refcheck.validators import file_exists


@pytest.fixture
def mock_settings_absolute_path():
    with mock.patch("refcheck.validators.settings") as mock_settings:
        mock_settings.allow_absolute = True
        yield mock_settings


@pytest.fixture
def mock_os_path_exists():
    with mock.patch("os.path.exists") as mock_exists:
        yield mock_exists


@pytest.fixture
def mock_os_path_abspath():
    with mock.patch("os.path.abspath") as mock_abspath:
        yield mock_abspath


# === Test cases for relative paths ===


def test_file_exists_simple_relative_path(mock_os_path_exists):
    mock_os_path_exists.return_value = True
    result = file_exists("some/path/origin.md", "relative_file.md")
    assert result is True
    mock_os_path_exists.assert_called_once_with(os.path.join("some/path", "relative_file.md"))


def test_file_does_not_exist_simple_relative_path(mock_os_path_exists):
    mock_os_path_exists.return_value = False
    result = file_exists("some/path/origin.md", "relative_file.md")
    assert result is False
    mock_os_path_exists.assert_called_once_with(os.path.join("some/path", "relative_file.md"))


def test_file_exists_relative_path_in_subdirectory(mock_os_path_exists):
    mock_os_path_exists.side_effect = lambda path: path in [os.path.join("some/path", "subdir/relative_file.md")]
    result = file_exists("some/path/origin.md", "subdir/relative_file.md")
    assert result is True
    mock_os_path_exists.assert_called_once_with(os.path.join("some/path", "subdir/relative_file.md"))


def test_file_does_not_exist_relative_path_in_subdirectory(mock_os_path_exists):
    mock_os_path_exists.side_effect = lambda path: False

    result = file_exists("some/path/origin.md", "subdir/relative_file.md")

    assert result is False
    assert mock_os_path_exists.call_count >= 1


# === Absolute Windows paths ===


def test_file_exists_absolute_windows_path(mock_os_path_exists):
    mock_os_path_exists.side_effect = lambda path: path == "relative_file.md"
    result = file_exists("some/path/origin.md", r"\relative_file.md")
    assert result is True
    mock_os_path_exists.assert_called_once_with("relative_file.md")


def test_file_does_not_exist_absolute_windows_path(mock_os_path_exists):
    mock_os_path_exists.side_effect = lambda path: False
    result = file_exists("some/path/origin.md", r"\relative_file.md")
    assert result is False
    mock_os_path_exists.assert_called_once_with("relative_file.md")


# === Absolute paths ===


def test_file_exists_absolute_path(mock_os_path_exists, mock_os_path_abspath, mock_settings_absolute_path):
    # Mock the behavior of os.path.exists for absolute paths
    mock_os_path_exists.side_effect = lambda path: path in [
        "/absolute/path/file.md",  # Simulate that this file exists
        "/absolute/path/relative_file.md",
    ]
    mock_os_path_abspath.return_value = "/absolute/path/file.md"  # Mock the absolute path of the origin file

    result = file_exists("/origin/path/origin.md", "/absolute/path/file.md")  # Check for an absolute path

    assert result is True  # Expecting True since the file exists
    assert mock_os_path_abspath.call_count >= 1  # Ensure abspath was called
    assert mock_os_path_exists.call_count >= 1  # Ensure exists was called


def test_file_does_not_exist_absolute_path(mock_os_path_exists, mock_os_path_abspath, mock_settings_absolute_path):
    mock_os_path_exists.return_value = False
    mock_os_path_abspath.return_value = "/absolute/path/file.md"

    result = file_exists("some/path/origin.md", "/relative_file.md")

    assert result is False
    assert mock_os_path_abspath.call_count >= 1
    assert mock_os_path_exists.call_count >= 1


def test_file_exists_absolute_path_in_subdirectory(
    mock_os_path_exists, mock_os_path_abspath, mock_settings_absolute_path
):
    # Test if the function can correctly identify an absolute reference path that is actually relative to the file where
    # the reference was made in.
    #
    # Example:
    # - Folder structure:
    #   -> C:/Users/user/repo/file.md
    #   -> C:/Users/user/repo/docs/other_file.md
    # - Input:
    #   -> Origin file: `C:/Users/user/repo/file.md`
    #   -> Reference: `/docs/other_file.md`
    #
    # The reference path `/docs/other_file.md` seems to be an absolute path, but it is actually a relative path to the
    # root  of `repo` in which the `file.md` is located. This is valid reference syntax. Therefore, the function should
    # check if the file exists at the following locations:
    #   1. `C:/docs/other_file.md` (Absolute path)
    #   2. `C:/Users/user/repo/docs/other_file.md`

    mock_os_path_exists.side_effect = lambda path: path in [
        "/absolute/path/file.md",
        "/absolute/path/subdir/relative_file.md",
        "/origin/path/subdir/relative_file.md",
        "/subdir/relative_file.md",
    ]

    mock_os_path_abspath.side_effect = lambda path: {
        "/origin/path/subdir/relative_file.md": "/absolute/path/subdir/relative_file.md",
        "/origin/path/origin.md": "/absolute/path/file.md",
    }.get(path, path)

    result = file_exists("/origin/path/origin.md", "/subdir/relative_file.md")

    assert result is True
    assert mock_os_path_abspath.call_count >= 1
    assert mock_os_path_exists.call_count >= 1


def test_file_exists_traverse_up_directory_tree(
    mock_os_path_exists, mock_os_path_abspath, mock_settings_absolute_path
):
    # Test if the function can correctly traverse up the directory tree to find the referenced file that is relative to
    # the root of the directories where the `origin.md` is located.
    #
    # Example:
    # /absolute/path/
    # ├── file.md
    # ├── relative_file.md
    # └── subdir/
    #     └── origin.md
    #
    # - Input:
    #   -> Origin file: `/origin/path/subdir/origin.md`
    #   -> Reference path: `/relative_file.md`
    #
    # If the `file_exists()` function works as intened it should proceed like this:
    # - The reference path `/relative_file.md` is treated as an absolute path initially.
    # - If not found as an absolute path, it treats it as a path related to the directories above the origin file.
    # Therefore, the function should check if the file exists at the following locations:
    #   1. `/relative_file.md` (Absolute path)
    #   2. `/absolute/path/relative_file.md` (Relative path traversing up the tree from
    #       `/absolute/path/subdir/origin.md`)
    #
    # The expected behavior is to successfully find the `relative_file.md` file while traversing up the tree.

    mock_os_path_exists.side_effect = lambda path: path in [
        "/absolute/path/file.md",  # Simulating that this file exists
        "/absolute/path/relative_file.md",  # Simulating that this file exists as relative path in the parent directory
    ]

    mock_os_path_abspath.return_value = "/absolute/path/file.md"  # Mocking the absolute path of the origin file

    # Calling the file_exists function with:
    # - An origin file path of `/origin/path/subdir/origin.md`
    # - A reference path of `/relative_file.md`
    result = file_exists("/origin/path/subdir/origin.md", "/relative_file.md")

    # Asserting that the result is True, indicating that the file was found
    assert result is True

    # Asserting that os.path.abspath was called at least once
    # This ensures that the function attempts to convert the path to absolute at some point
    assert mock_os_path_abspath.call_count >= 1

    # Asserting that os.path.exists was called at least once
    # This checks if the function actually checked for file existence
    assert mock_os_path_exists.call_count >= 1


# === Edge cases such as invalid paths or unusual formats ===


def test_file_invalid_path(mock_os_path_exists):
    mock_os_path_exists.return_value = False

    result = file_exists("some/path/origin.md", "invalid_path.json?query=string")

    assert result is False
    mock_os_path_exists.assert_called_once()


def test_file_valid_path_with_query_string(mock_os_path_exists):
    mock_os_path_exists.return_value = True

    result = file_exists("some/path/origin.md", "valid_path.md?query=string")

    assert result is True
    mock_os_path_exists.assert_called_once()
