import os
import logging

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


def load_exclusion_patterns() -> list:
    """Read exclusions from the .refcheckignore file."""
    if not os.path.isfile(IGNORE_FILE):
        logger.warning(f"Could not find {IGNORE_FILE}. Using default exclusions.")
        exclusions = CHECK_IGNORE_DEFAULTS
    else:
        logger.info(f"Reading exclusions from {IGNORE_FILE}...")
        with open(IGNORE_FILE, "r", encoding="utf-8") as file:
            exclusions = [line.strip() for line in file if line.strip()]

    print(f"[!] WARNING: Will skip these files and directories: {exclusions}")
    return exclusions


def get_markdown_files_from_dir(root_dir: str, exclude: list[str] = []) -> list:
    """Traverse the directory to get all markdown files."""
    print(f"[+] Searching for markdown files in {os.path.abspath(root_dir)} ...")
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


def get_markdown_files_from_args(paths: list[str], exclude: list[str] = []) -> list:
    """Retrieve all markdown files specified by the user."""
    # Read additional exclusions from the ignore file
    exclude += load_exclusion_patterns()

    exclude_set = set(os.path.normpath(path) for path in exclude)
    markdown_files = set()

    for path in paths:
        norm_path = os.path.normpath(path)
        if norm_path in exclude_set:
            continue
        if os.path.isdir(norm_path):
            markdown_files.update(get_markdown_files_from_dir(norm_path, exclude))
        elif os.path.isfile(norm_path):
            if norm_path.endswith(".md"):
                markdown_files.add(norm_path)
        else:
            print(f"[!] Warning: {path} is not a valid file or directory.")

    return list(markdown_files)


def print_green_background(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[42m{text}\033[0m"


def print_red_background(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[41m{text}\033[0m"


def print_red(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[31m{text}\033[0m"


def print_green(text: str, no_color: bool = False) -> str:
    return text if no_color else f"\033[32m{text}\033[0m"
