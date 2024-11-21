import os
import argparse


def get_markdown_files_from_dir(root_dir: str) -> list:
    """Traverse the directory to get all markdown files."""
    markdown_files = []

    # Walk through the directory to get all markdown files
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(subdir, file))

    return markdown_files


def get_markdown_files_from_args(files: list[str], directories: list[str]) -> list:
    """Retrieve all markdown files specified by the user."""
    markdown_files = set(files)  # remove duplicates

    if directories:
        for directory in directories:
            markdown_files.update(get_markdown_files_from_dir(directory))
    return list(markdown_files)


def setup_arg_parser():
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(description="Tool to check links and local references in Markdown files.")
    parser.add_argument("files", metavar="FILE", type=str, nargs="*", default=[], help="Markdown files to check")
    parser.add_argument(
        "-d",
        "--directories",
        metavar="DIRECTORY",
        type=str,
        nargs="*",
        default=[],
        help="Directories to traverse for Markdown files",
    )
    parser.add_argument("-n", "--no-color", action="store_true", help="Turn off colored output")
    return parser


def print_green_background(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[42m{text}\033[0m"


def print_red_background(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[41m{text}\033[0m"


def print_red(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[31m{text}\033[0m"


def print_green(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[32m{text}\033[0m"
