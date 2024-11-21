import os
import re
import requests

# Disable verify warnings for HTTPS requests
requests.packages.urllib3.disable_warnings()  # type: ignore


def is_valid_remote_reference(url: str) -> bool:
    """Check if online references are reachable."""
    try:
        response = requests.head(url, timeout=5, verify=False)
        if response.status_code >= 400:
            return False
    except Exception:
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
    """Check if markdown references are reachable."""
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
