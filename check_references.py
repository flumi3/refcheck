import os
import re
import requests
from re import Pattern

# Define the root directory to scan
ROOT_DIR = "./"

# ================= REGEX PATTERNS FOR PARSING MARKDOWN FILES ==================

# HTTP/HTTPS Links - inline, footnotes, and remote images
HTTP_LINK_PATTERN = re.compile(r"\[(.*?)\]\((https?://.*?)\)")  # all links in []() and ![]()
INLINE_LINK_PATTERN = re.compile(r"<(https?://\S+)>")  # <http://example.com>
RAW_LINK_PATTERN = re.compile(r"(^| )(?:(https?://\S+))")  # all links that are surrounded by nothing or spaces
HTML_LINK_PATTERN = re.compile(r"<a\s+(?:[^>]*?\s+)?href=([\"\'])(.*?)\1")  # <a href="http://example.com">

# Local File References - scripts, markdown files, and local images
FILE_PATTERN = re.compile(r"\[(.*?)\]\((?!http)(.*?)\)")  # all local files in []() and ![]()
HTML_IMAGE_PATTERN = re.compile(r'<img\s+(?:[^>]*?\s+)?src=(["\'])(.*?)\1')  # <img src="image.png">

# ==============================================================================


def get_markdown_files(root_dir):
    """Traverse the directory to get all markdown files."""
    markdown_files = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(subdir, file))
    return markdown_files


def parse_markdown_file(file_path):
    """Parse a markdown file to extract references."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    http_links = find_matches_with_line_numbers(HTTP_LINK_PATTERN, content, group=2)
    inline_links = find_matches_with_line_numbers(INLINE_LINK_PATTERN, content)
    raw_links = find_matches_with_line_numbers(RAW_LINK_PATTERN, content, group=2)
    html_links = find_matches_with_line_numbers(HTML_LINK_PATTERN, content, group=2)
    file_refs = find_matches_with_line_numbers(FILE_PATTERN, content, group=2)
    html_images = find_matches_with_line_numbers(HTML_IMAGE_PATTERN, content, group=2)

    return {
        "http_links": http_links,
        "inline_links": inline_links,
        "raw_links": raw_links,
        "html_links": html_links,  # returns list of (link, line_number) tuples
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


def is_valid_remote_reference(url: str) -> bool:
    """Check if online references are reachable."""
    try:
        response = requests.head(url, timeout=5, verify=False)
        if response.status_code >= 400:
            return False
    except Exception as e:
        return False
    else:
        return True


def is_valid_local_reference(ref: str, base_path: str) -> bool:
    """Check if local references are reachable."""
    asset_path = os.path.join(base_path, ref)
    return os.path.exists(asset_path)


def normalize_header(header: str) -> str:
    """Normalize header to match Markdown link format."""
    return header.strip().lower().replace(" ", "-")


def is_valid_markdown_reference(ref: str, base_path: str) -> bool:
    """Check if markdown references are reachable.
    Markdown references can be either a file path or a file path with a header link.
    Some examples:
    - docs/README.md
    - docs/README.md#getting-started
    """

    if "#" in ref:
        file_path, header_link = ref.split("#", 1)
    else:
        file_path = ref
        header_link = None

    target_path = os.path.join(base_path, file_path)
    if not os.path.exists(target_path):
        return False

    if header_link:
        with open(target_path, "r", encoding="utf-8") as file:
            target_content = file.read()
            normalized_header_link = normalize_header(header_link)
            normalized_headers = re.findall(r"^#{1,6}\s+(.*)", target_content, re.MULTILINE)
            normalized_headers = [normalize_header(header) for header in normalized_headers]
            if normalized_header_link not in normalized_headers:
                return False

    return True


def print_green(text: str):
    return f"\033[42m{text}\033[0m"


def print_red(text: str):
    return f"\033[41m{text}\033[0m"


def main():
    broken_references = []  # Collect broken references with line numbers

    print("[+] Searching for Markdown files in the given directory...")
    all_files = get_markdown_files(ROOT_DIR)
    print(f"Found {len(all_files)} Markdown files:")
    for file in all_files:
        print(f" - {file}")

    for file in all_files:
        print(f"\n[+] Checking {file}...")
        base_path = os.path.dirname(file)
        references = parse_markdown_file(file)

        # Combine remote references
        remote_refs = (
            references["http_links"] + references["inline_links"] + references["raw_links"] + references["html_links"]
        )
        # Combine local references
        local_refs = references["file_refs"] + references["html_images"]

        # Validate remote references
        for url, line_num in remote_refs:
            if is_valid_remote_reference(url):
                print(f"{file}:{line_num}: {url} - {print_green('OK')}")
            else:
                print(f"{file}:{line_num}: {url} - {print_red('BROKEN')}")
                broken_references.append((file, url, line_num))

        # Validate local references
        for ref, line_num in local_refs:
            if (".md" in ref and is_valid_markdown_reference(ref, base_path)) or is_valid_local_reference(ref, base_path):  # fmt: skip
                print(f"{file}:{line_num}: {ref} - {print_green('OK')}")
            else:
                print(f"{file}:{line_num}: {ref} - {print_red('BROKEN')}")
                broken_references.append((file, ref, line_num))

    # Summary of broken references
    if broken_references:
        print("\n[!] Broken references found:")

        # Sort broken references by line number
        broken_references = sorted(broken_references, key=lambda x: x[2])

        for file, ref, line_num in broken_references:
            # Format output for easy navigation in VSCode
            print(f"{file}:{line_num}: {ref}")

    print("\nReference check complete.")


if __name__ == "__main__":
    main()
