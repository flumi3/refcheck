import os
import sys
import logging
from typing import List, Tuple

from refcheck.log_conf import setup_logging
from refcheck.parsers import parse_markdown_file
from refcheck.validators import is_valid_remote_reference, file_exists, is_valid_markdown_reference
from refcheck.utils import (
    get_markdown_files_from_args,
    setup_arg_parser,
    print_green_background,
    print_red_background,
    print_red,
    print_green,
)

logger = logging.getLogger()

Reference = Tuple[str, str, int]


def main() -> bool:
    parser = setup_arg_parser()
    args = parser.parse_args()

    # Check if the user has provided any files or directories
    if not args.files and not args.directories:
        parser.print_help()
        return False

    setup_logging(verbose=args.verbose)  # Setup logging based on the --verbose flag
    no_color = args.no_color

    # Retrieve all markdown files specified by the user
    markdown_files = get_markdown_files_from_args(args.files, args.directories, args.exclude)
    if not markdown_files:
        print("[!] No Markdown files specified or found.")
        return False

    print(f"[+] {len(markdown_files)} Markdown files to check.")
    for file in markdown_files:
        print(f"- {file}")

    broken_references: List[Reference] = []

    for file in markdown_files:
        print(f"\n[+] Checking {file}...")
        references = parse_markdown_file(file)

        remote_refs = (
            references["http_links"] + references["inline_links"] + references["raw_links"] + references["html_links"]
        )
        local_refs = references["file_refs"] + references["html_images"]

        if not remote_refs and not local_refs:
            print("-> No references found.")
            continue

        if args.check_remote:
            check_remote_references(file, remote_refs, broken_references, no_color)
        else:
            logger.warning("Skipping remote reference check. Enable with arg --check-remote.")

        check_local_references(file, local_refs, broken_references, no_color)

    print_summary(broken_references, no_color)
    return not bool(broken_references)


def check_remote_references(
    file: str, remote_refs: List[Tuple[str, int]], broken_references: List[Reference], no_color: bool
) -> None:
    logger.info("Checking remote references...")
    for url, line_num in remote_refs:
        logger.info(f"Checking remote reference: {url}")
        if is_valid_remote_reference(url):
            status = print_green_background("OK", no_color)
        else:
            status = print_red_background("BROKEN", no_color)
            broken_references.append((file, url, line_num))
        print(f"{file}:{line_num}: {url} - {status}")


def check_local_references(
    file: str, local_refs: List[Tuple[str, int]], broken_references: List[Reference], no_color: bool
) -> None:
    for ref, line_num in local_refs:
        logger.info(f"Checking local reference: {ref}")
        if ".md" in ref or "#" in ref:
            check_markdown_reference(file, ref, line_num, broken_references, no_color)
        else:
            check_asset_reference(file, ref, line_num, broken_references, no_color)


def check_markdown_reference(
    file: str, ref: str, line_num: int, broken_references: List[Reference], no_color: bool
) -> None:
    if is_valid_markdown_reference(ref, file):
        status = print_green_background("OK", no_color)
    else:
        status = print_red_background("BROKEN", no_color)
        broken_references.append((file, ref, line_num))
    print(f"{file}:{line_num}: {ref} - {status}")


def check_asset_reference(
    file: str, ref: str, line_num: int, broken_references: List[Reference], no_color: bool
) -> None:
    asset_path = os.path.join(os.path.dirname(file), ref)
    if file_exists(asset_path):
        status = print_green_background("OK", no_color)
    else:
        status = print_red_background("BROKEN", no_color)
        broken_references.append((file, ref, line_num))
    print(f"{file}:{line_num}: {ref} - {status}")


def print_summary(broken_references: List[Reference], no_color: bool) -> None:
    print("\nReference check complete.")
    print("\n============================| Summary |=============================")

    if broken_references:
        print(print_red(f"[!] {len(broken_references)} broken references found:", no_color))

        broken_references = sorted(broken_references, key=lambda x: (x[0], x[2]))

        for file, ref, line_num in broken_references:
            print(f"{file}:{line_num}: {ref}")
    else:
        print(print_green("\U0001F389 No broken references.", no_color))

    print("==================================================================")


if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
