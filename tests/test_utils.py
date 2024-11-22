import os
import pytest
from unittest.mock import patch, MagicMock
from refcheck.utils import (
    get_markdown_files_from_dir,
    get_markdown_files_from_args,
    print_green_background,
    print_red_background,
    print_red,
    print_green,
)


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


def test_get_markdown_files_from_args():
    with patch("refcheck.utils.get_markdown_files_from_dir") as mock_get_markdown_files_from_dir:
        # Mock get_markdown_files_from_dir function to return the following files:
        # dir1
        # └── file1.md
        # dir2
        # └── file2.md
        mock_get_markdown_files_from_dir.return_value = [
            os.path.normpath("dir1/file1.md"),
            os.path.normpath("dir2/file2.md"),
        ]

        result = get_markdown_files_from_args(
            files=[os.path.normpath("file3.md")],
            directories=[os.path.normpath("dir1"), os.path.normpath("dir2")],
        )
        expected = [os.path.normpath("file3.md"), os.path.normpath("dir1/file1.md"), os.path.normpath("dir2/file2.md")]
        assert set(result) == set(expected)


def test_print_green_background():
    result = print_green_background("Test", no_color=False)
    expected = "\033[42mTest\033[0m"
    assert result == expected


def test_print_red_background():
    result = print_red_background("Test", no_color=False)
    expected = "\033[41mTest\033[0m"
    assert result == expected


def test_print_red():
    result = print_red("Test", no_color=False)
    expected = "\033[31mTest\033[0m"
    assert result == expected


def test_print_green():
    result = print_green("Test", no_color=False)
    expected = "\033[32mTest\033[0m"
    assert result == expected


def test_print_with_no_color():
    assert print_green_background("Test", no_color=True) == "Test"
    assert print_red_background("Test", no_color=True) == "Test"
    assert print_red("Test", no_color=True) == "Test"
    assert print_green("Test", no_color=True) == "Test"


if __name__ == "__main__":
    pytest.main()
