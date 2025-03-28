import os
import pytest
from unittest.mock import patch
from refcheck.utils import (
    get_markdown_files_from_dir,
    get_markdown_files_from_args,
    print_green_background,
    print_red_background,
    print_red,
    print_green,
    print_yellow
)


# === Test get_markdown_files_from_dir ===


def test_get_markdown_files_from_dir():
    with patch("os.walk") as mock_walk:
        # Mock folder structure for testing, which is returned by os.walk:
        # root
        # ├── subdir1
        # │   └── file3.md
        # └── subdir2
        #     ├── file4.txt
        #     └── file5.md
        # ├── file1.md
        # └── file2.py
        mock_walk.return_value = [
            (os.path.normpath("root"), ("subdir1", "subdir2"), ("file1.md", "file2.py")),
            (os.path.normpath("root/subdir1"), (), ("file3.md",)),
            (os.path.normpath("root/subdir2"), (), ("file4.txt", "file5.md")),
        ]

        # Test case 1: No exclude
        result = get_markdown_files_from_dir("root")
        expected = [
            os.path.normpath("root/file1.md"),
            os.path.normpath("root/subdir1/file3.md"),
            os.path.normpath("root/subdir2/file5.md"),
        ]
        assert result == expected

        # Test case 2: Exclude directory root/subdir1
        result = get_markdown_files_from_dir("root", exclude=["root/subdir1"])
        expected = [os.path.normpath("root/file1.md"), os.path.normpath("root/subdir2/file5.md")]
        assert result == expected

        # Test case 3: Exclude file root/subdir1/file3.md
        result = get_markdown_files_from_dir("root", exclude=["root/subdir1/file3.md"])
        expected = [
            os.path.normpath("root/file1.md"),
            os.path.normpath("root/subdir2/file5.md"),
        ]


# === Test get_markdown_files_from_args ===


# Mock function for loading exclusion patterns
def mock_load_exclusion_patterns():
    return ["excluded.md"]


# Mock function for getting markdown files from directory
def mock_get_markdown_files_from_dir(directory, exclude):
    return {"dir_file.md"}


# Mock os.path functions to prevent filesystem dependency
def mock_os_path_isdir(path):
    # Mock directories based on the provided paths
    return path == "dir"


def mock_os_path_isfile(path):
    # Mock files based on the provided paths
    return path in ["file1.md", "file2.md", "excluded.md", "dir_file.md"]


def mock_os_path_normpath(path):
    # Return the path as is for simplicity
    return path


# Single test function to cover multiple cases
@pytest.mark.parametrize(
    "paths, exclude, expected_files, expected_warnings",
    [
        (["file1.md", "file2.md"], [], ["file1.md", "file2.md"], []),
        (["file1.md", "dir"], [], ["file1.md", "dir_file.md"], []),
        (["file1.md", "excluded.md"], [], ["file1.md"], []),
        (["file1.md", "invalid_path"], [], ["file1.md"], ["invalid_path is not a valid file or directory."]),
    ],
)
def test_get_markdown_files_from_args(paths, exclude, expected_files, expected_warnings, monkeypatch, capsys):
    # Apply mocks
    monkeypatch.setattr("refcheck.utils.load_exclusion_patterns", mock_load_exclusion_patterns)
    monkeypatch.setattr("refcheck.utils.get_markdown_files_from_dir", mock_get_markdown_files_from_dir)
    monkeypatch.setattr(os.path, "isdir", mock_os_path_isdir)
    monkeypatch.setattr(os.path, "isfile", mock_os_path_isfile)
    monkeypatch.setattr(os.path, "normpath", mock_os_path_normpath)

    # Run the function
    result = get_markdown_files_from_args(paths, exclude)

    # Check the result
    assert sorted(result) == sorted(expected_files)

    # Check for warnings if any
    captured = capsys.readouterr()
    for warning in expected_warnings:
        assert warning in captured.out


# === Test print functions ===

@pytest.fixture
def mock_settings_no_color_true():
    with patch('refcheck.utils.settings') as mock_settings:
        mock_settings.no_color = True
        yield mock_settings

@pytest.fixture
def mock_settings_no_color_false():
    with patch('refcheck.utils.settings') as mock_settings:
        mock_settings.no_color = False
        yield mock_settings

# Green background

def test_print_green_background_no_color(mock_settings_no_color_true):
    result = print_green_background("test")
    assert result == "test"

def test_print_green_background_color(mock_settings_no_color_false):
    result = print_green_background("test")
    assert result == "\033[42mtest\033[0m"

# Red background

def test_print_red_background_no_color(mock_settings_no_color_true):
    result = print_red_background("test")
    assert result == "test"

def test_print_red_background_color(mock_settings_no_color_false):
    result = print_red_background("test")
    assert result == "\033[41mtest\033[0m"

# Red

def test_print_red_no_color(mock_settings_no_color_true):
    result = print_red("test")
    assert result == "test"

def test_print_red_color(mock_settings_no_color_false):
    result = print_red("test")
    assert result == "\033[31mtest\033[0m"

# Green

def test_print_green_no_color(mock_settings_no_color_true):
    result = print_green("test")
    assert result == "test"

def test_print_green_color(mock_settings_no_color_false):
    result = print_green("test")
    assert result == "\033[32mtest\033[0m"

# Yellow

def test_print_yellow_no_color(mock_settings_no_color_true):
    result = print_yellow("test")
    assert result == "test"

def test_print_yellow_color(mock_settings_no_color_false):
    result = print_yellow("test")
    assert result == "\033[33mtest\033[0m"


if __name__ == "__main__":
    pytest.main()
