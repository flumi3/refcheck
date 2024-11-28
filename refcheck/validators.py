import os
import re
import logging
import requests

from refcheck.parsers import Reference

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


def file_exists(origin_file_path: str, ref_file_path: str) -> bool:
    """Check if local file exists."""
    logger.info(f"Checking if file exists: {ref_file_path}")

    file_exists = False

    if ref_file_path.startswith("\\"):
        # This seems to be an absolute windows path (e.g. \file.md) but it's actually a relative path to the
        # file where the reference was made in. (I know, strange that this is valid...)
        logger.info("Seemingly absolute reference path starts with backslash. Treating as relative path ...")
        relative_ref = ref_file_path[1:]  # Remove leading backslash
        logger.info(f"{ref_file_path} -> {relative_ref}")
        if os.path.exists(relative_ref):
            file_exists = True
        else:
            logger.info("File does not exist.")

    elif ref_file_path.startswith("/"):
        # This is an absolute path. We have to check if the file exists at the absolute path or as a path relative to
        # every possible subpart of the origin file path.
        logger.warning("Reference is absolute.")

        # First, test the file with the absolute path
        logger.info("Checking if the file exists as an absolute path ...")
        abs_ref_path = os.path.abspath(ref_file_path)
        logger.info(f"-> '{abs_ref_path}'")
        if os.path.exists(abs_ref_path):
            file_exists = True
        else:
            logger.info("File does not exist as an absolute path.")
            # Strip the leading slash to convert the path to a relative path
            ref = ref_file_path[1:]

            # Get the absolute path of the file where the reference was made in, e.g., C:/Users/user/repo/docs/file.md
            absolute_file_path = os.path.abspath(origin_file_path)

            # Check if the file exists relative to the file in which the reference was made in
            logger.info("Checking if the path exists relative to the file in which the reference was made in ...")
            abs_ref_path = os.path.join(os.path.dirname(absolute_file_path), ref)
            logger.info(f"-> '{abs_ref_path}'.")

            if os.path.exists(abs_ref_path):
                file_exists = True
            else:
                # Traverse up the directory tree and test the relative path for each directory until we either
                # find the file, or cannot go up any further.
                logger.info("File does not exists there. Moving up the directory tree to find the file ...")

                starting_dir = os.path.dirname(absolute_file_path)
                while True:
                    parent_dir = os.path.dirname(starting_dir)
                    abs_ref_path = os.path.join(parent_dir, ref)
                    logger.info(f"-> {abs_ref_path}")
                    if os.path.exists(abs_ref_path):
                        file_exists = True
                        break
                    else:
                        logger.info("File does not exist. Moving up the directory tree ...")
                        if parent_dir == starting_dir:
                            logger.info("Reached the root of the repository. Stopping search.")
                            break

                        starting_dir = parent_dir
    else:
        # It is a simple relative path. Check if the file exists relative to the file in which the reference was made in
        ref_file_path = os.path.join(os.path.dirname(origin_file_path), ref_file_path)
        logger.info(f"Path to check: {ref_file_path}")
        if os.path.exists(ref_file_path):
            file_exists = True

    if file_exists:
        logger.info("File exists!")
        return True
    else:
        logger.info("File does not exist.")
        return False


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


def is_valid_markdown_reference(ref: Reference) -> bool:
    """Check if markdown references are reachable.

    Args:
        ref (Reference): Reference object containing the reference information.

    Returns:
        bool: True if the reference is valid and reachable, False otherwise.
    """
    if ref.link.startswith("#"):
        logger.info("Reference is a header in the same Markdown file.")
        referenced_header = ref.link[1:]  # Remove leading `#`
        target_path = ref.file_path
    elif "#" in ref.link:
        logger.info("Reference is a header in another Markdown file.")
        referenced_file, referenced_header = ref.link.split("#", 1)
        target_path = referenced_file
    else:
        # Reference is a Markdown file
        referenced_file = ref.link
        referenced_header = None
        target_path = referenced_file

    # Check if the referenced file exists
    if not ref.link.startswith("#"):  # Skip if the reference is a header in the same file because the file exists
        if not file_exists(ref.file_path, target_path):
            return False

    # Check if the referenced header exists
    if referenced_header and not header_exists(target_path, referenced_header):
        logger.error(f"Referenced header does not exist in {target_path}: {referenced_header}")
        return False

    return True
