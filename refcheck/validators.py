import os
import re
import logging
import requests

# Disable verify warnings for HTTPS requests
requests.packages.urllib3.disable_warnings()  # type: ignore

logger = logging.getLogger()


def is_valid_remote_reference(url: str) -> bool:
    """Check if online references are reachable."""
    try:
        response = requests.head(url, timeout=5, verify=False)
        if response.status_code >= 400:
            return False
    except Exception:
        logger.exception(f"Exception occurred while checking URL: {url}")
        return False
    else:
        return True


def file_exists(file_path: str) -> bool:
    """Check if local file exists."""
    exists = os.path.exists(file_path)
    if not exists:
        logger.warning(f"File does not exist: {file_path}")
    return exists


def header_exists(file_path: str, header: str) -> bool:
    """Check if Markdown header exists in the given file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            normalized_header = normalize_header(header)
            normalized_headers = [normalize_header(h) for h in re.findall(r"^#{1,6}\s+(.*)", content, re.MULTILINE)]
            if normalized_header in normalized_headers:
                return True
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    return False


def normalize_header(header: str) -> str:
    """Normalize header to match Markdown link format."""
    return re.sub(r"[^a-zA-Z0-9 -]", "", header.strip().lower().replace(" ", "-"))


def is_valid_markdown_reference(ref: str, file_path: str) -> bool:
    """Check if markdown references are reachable.

    Args:
        ref: The reference to check, e.g. `file.md#header`, `#header`, `file.md`.
        file_path: The path of the file where the reference was made in.

    Returns:
        bool: True if the reference is valid and reachable, False otherwise.
    """
    base_path = os.path.dirname(file_path)  # Directory of the file

    if ref.startswith("#"):
        logger.info("Reference is a header in the same Markdown file.")
        referenced_file = file_path
        referenced_header = ref[1:]  # Remove leading `#`
    elif "#" in ref:
        logger.info("Reference is a header in another Markdown file.")
        referenced_file, referenced_header = ref.split("#", 1)
    else:
        logger.info("Reference is to another Markdown file.")
        referenced_file = ref
        referenced_header = None

    # Check if the referenced file exists
    target_path = os.path.join(base_path, referenced_file)
    if not file_exists(target_path):
        logger.error(f"Referenced file does not exist: {target_path}")
        return False

    # Check if the referenced header exists
    if referenced_header and not header_exists(target_path, referenced_header):
        logger.error(f"Referenced header does not exist in {target_path}: {referenced_header}")
        return False

    return True
