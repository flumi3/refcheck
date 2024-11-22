import os
import sys
import logging
from typing import List, Tuple
from dataclasses import dataclass

from refcheck.log_conf import setup_logging
from refcheck.parsers import parse_markdown_file, init_arg_parser
from refcheck.validators import is_valid_remote_reference, file_exists, is_valid_markdown_reference
from refcheck.utils import (
    get_markdown_files_from_args,
    print_green_background,
    print_red_background,
    print_red,
    print_green,
)

logger = logging.getLogger()


@dataclass
class Reference:
    file: str
    ref: str
    line_num: int


@dataclass
class BrokenReference(Reference):
    status: str


class ReferenceChecker:
    def __init__(self, no_color: bool):
        self.no_color = no_color
        self.broken_references: List[BrokenReference] = []

    def check_remote_references(self, file: str, remote_refs: List[Tuple[str, int]]):
        logger.info("Checking remote references...")
        for url, line_num in remote_refs:
            logger.info(f"Checking remote reference: {url}")
            if is_valid_remote_reference(url):
                status = print_green_background("OK", self.no_color)
            else:
                status = print_red_background("BROKEN", self.no_color)
                self.broken_references.append(BrokenReference(file, url, line_num, status))
            print(f"{file}:{line_num}: {url} - {status}")

    def check_local_references(self, file: str, local_refs: List[Tuple[str, int]]):
        for ref, line_num in local_refs:
            logger.info(f"Checking local reference: {ref}")
            if ".md" in ref or "#" in ref:
                self.check_markdown_reference(file, ref, line_num)
            else:
                self.check_asset_reference(file, ref, line_num)

    def check_markdown_reference(self, file: str, ref: str, line_num: int):
        if is_valid_markdown_reference(ref, file):
            status = print_green_background("OK", self.no_color)
        else:
            status = print_red_background("BROKEN", self.no_color)
            self.broken_references.append(BrokenReference(file, ref, line_num, status))
        print(f"{file}:{line_num}: {ref} - {status}")

    def check_asset_reference(self, file: str, ref: str, line_num: int):
        asset_path = os.path.join(os.path.dirname(file), ref)
        if file_exists(asset_path):
            status = print_green_background("OK", self.no_color)
        else:
            status = print_red_background("BROKEN", self.no_color)
            self.broken_references.append(BrokenReference(file, ref, line_num, status))
        print(f"{file}:{line_num}: {ref} - {status}")

    def print_summary(self):
        print("\nReference check complete.")
        print("\n============================| Summary |=============================")

        if self.broken_references:
            print(print_red(f"[!] {len(self.broken_references)} broken references found:", self.no_color))
            self.broken_references = sorted(self.broken_references, key=lambda x: (x.file, x.line_num))

            for broken_ref in self.broken_references:
                print(f"{broken_ref.file}:{broken_ref.line_num}: {broken_ref.ref}")
        else:
            print(print_green("\U0001F389 No broken references.", self.no_color))

        print("====================================================================")


def main() -> bool:
    parser = init_arg_parser()
    args = parser.parse_args()

    # Check if the user has provided any files or directories
    if not args.paths:
        parser.print_help()
        return False

    setup_logging(verbose=args.verbose)  # Setup logging based on the --verbose flag
    no_color = args.no_color

    # Retrieve all markdown files specified by the user
    markdown_files = get_markdown_files_from_args(args.paths, args.exclude)
    if not markdown_files:
        print("[!] No Markdown files specified or found.")
        return False

    print(f"[+] {len(markdown_files)} Markdown files to check.")
    for file in markdown_files:
        print(f"- {file}")

    checker = ReferenceChecker(no_color)

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
            checker.check_remote_references(file, remote_refs)
        else:
            logger.warning("Skipping remote reference check. Enable with arg --check-remote.")

        checker.check_local_references(file, local_refs)

    checker.print_summary()
    return not bool(checker.broken_references)


if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
