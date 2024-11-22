import re
import argparse
from re import Pattern

# HTTP/HTTPS Links - inline, footnotes, and remote images
HTTP_LINK_PATTERN = re.compile(r"\[(.*?)\]\((https?://.*?)\)")  # all links in []() and ![]()
INLINE_LINK_PATTERN = re.compile(r"<(https?://\S+)>")  # <http://example.com>
RAW_LINK_PATTERN = re.compile(r"(^| )(?:(https?://\S+))")  # all links that are surrounded by nothing or spaces
HTML_LINK_PATTERN = re.compile(r"<a\s+(?:[^>]*?\s+)?href=([\"\'])(.*?)\1")  # <a href="http://example.com">

# Local File References - scripts, markdown files, and local images
FILE_PATTERN = re.compile(r"\[(.*?)\]\((?!http)(.*?)\)")  # all local files in []() and ![]()
HTML_IMAGE_PATTERN = re.compile(r"<img\s+(?:[^>]*?\s+)?src=([\"\'])(.*?)\1")  # <img src="image.png">


def parse_markdown_file(file_path: str) -> dict:
    """Parse a markdown file to extract references."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return {}
    except IOError as e:
        print(f"Error: An I/O error occurred while reading the file {file_path}: {e}")
        return {}

    http_links = _find_matches_with_line_numbers(HTTP_LINK_PATTERN, content, group=2)
    inline_links = _find_matches_with_line_numbers(INLINE_LINK_PATTERN, content, group=1)
    raw_links = _find_matches_with_line_numbers(RAW_LINK_PATTERN, content, group=2)
    html_links = _find_matches_with_line_numbers(HTML_LINK_PATTERN, content, group=2)
    file_refs = _find_matches_with_line_numbers(FILE_PATTERN, content, group=2)
    html_images = _find_matches_with_line_numbers(HTML_IMAGE_PATTERN, content, group=2)

    return {
        "http_links": http_links,
        "inline_links": inline_links,
        "raw_links": raw_links,
        "html_links": html_links,
        "file_refs": file_refs,
        "html_images": html_images,
    }


def init_arg_parser():
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


def _find_matches_with_line_numbers(pattern: Pattern[str], text: str, group: int = 0) -> list:
    """Find regex matches along with their line numbers."""
    matches_with_line_numbers = []
    for match in re.finditer(pattern, text):
        start_pos = match.start(group)
        line_number = text.count("\n", 0, start_pos) + 1
        matches_with_line_numbers.append((match.group(group), line_number))
    return matches_with_line_numbers
