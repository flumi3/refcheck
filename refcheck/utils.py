import os
import logging
import argparse

logger = logging.getLogger()

IGNORE_FILE = ".refcheckignore"

CHECK_IGNORE_DEFAULTS = [
    ".git",
    ".vscode",
    ".idea",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    ".pytest_cache",
]


def read_exclusions_from_file() -> list:
    """Read exclusions from the .refcheckignore file."""
    if not os.path.isfile(IGNORE_FILE):
        logger.warning(f"Could not find {IGNORE_FILE}. Using default exclusions.")
        return CHECK_IGNORE_DEFAULTS

    with open(IGNORE_FILE, "r", encoding="utf-8") as file:
        exclusions = [line.strip() for line in file if line.strip()]
        logger.info(f"Read {len(exclusions)} exclusions from {IGNORE_FILE}.")

    logger.info(f"Exclusions: {exclusions}")
    return exclusions


def get_markdown_files_from_dir(root_dir: str, exclude: list[str] = []) -> list:
    """Traverse the directory to get all markdown files."""
    exclude_set = set(os.path.normpath(path) for path in exclude)
    markdown_files = []

    # Walk through the directory to get all markdown files
    for subdir, _, files in os.walk(root_dir):
        subdir_norm = os.path.normpath(subdir)
        if any(subdir_norm.startswith(exclude_item) for exclude_item in exclude_set):
            continue  # Skip excluded directories

        for file in files:
            file_path = os.path.join(subdir, file)
            file_path_norm = os.path.normpath(file_path)
            if file.endswith(".md") and file_path_norm not in exclude_set:
                markdown_files.append(file_path_norm)

    return markdown_files


def get_markdown_files_from_args(files: list[str], directories: list[str], exclude: list[str] = []) -> list:
    """Retrieve all markdown files specified by the user."""
    # Read additional exclusions from the ignore file
    exclude += read_exclusions_from_file()

    exclude_set = set(os.path.normpath(path) for path in exclude)
    markdown_files = set(os.path.normpath(file) for file in files if os.path.normpath(file) not in exclude_set)

    if directories:
        for directory in directories:
            markdown_files.update(get_markdown_files_from_dir(directory, exclude))
    return list(markdown_files)


def setup_arg_parser():
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(description="Tool for validating references in Markdown files.")
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
    parser.add_argument(
        "-e", "--exclude", metavar="EXCLUDE", type=str, nargs="*", default=[], help="Files or directories to exclude"
    )
    parser.add_argument("--check-remote", action="store_true", help="Check remote references (HTTP/HTTPS links)")
    parser.add_argument("-n", "--no-color", action="store_true", help="Turn off colored output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    return parser


def print_green_background(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[42m{text}\033[0m"


def print_red_background(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[41m{text}\033[0m"


def print_red(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[31m{text}\033[0m"


def print_green(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[32m{text}\033[0m"
