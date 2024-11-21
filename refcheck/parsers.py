import re
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
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    http_links = find_matches_with_line_numbers(HTTP_LINK_PATTERN, content, group=2)
    inline_links = find_matches_with_line_numbers(INLINE_LINK_PATTERN, content, group=1)
    raw_links = find_matches_with_line_numbers(RAW_LINK_PATTERN, content, group=2)
    html_links = find_matches_with_line_numbers(HTML_LINK_PATTERN, content, group=2)
    file_refs = find_matches_with_line_numbers(FILE_PATTERN, content, group=2)
    html_images = find_matches_with_line_numbers(HTML_IMAGE_PATTERN, content, group=2)

    return {
        "http_links": http_links,
        "inline_links": inline_links,
        "raw_links": raw_links,
        "html_links": html_links,
        "file_refs": file_refs,
        "html_images": html_images,
    }


def find_matches_with_line_numbers(pattern: Pattern[str], text: str, group: int = 0) -> list:
    """Find regex matches along with their line numbers."""
    matches_with_line_numbers = []
    for match in re.finditer(pattern, text):
        start_pos = match.start(group)
        line_number = text.count("\n", 0, start_pos) + 1
        matches_with_line_numbers.append((match.group(group), line_number))
    return matches_with_line_numbers
