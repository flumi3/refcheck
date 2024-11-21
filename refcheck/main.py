import os
import sys
from refcheck.parsers import parse_markdown_file
from refcheck.validators import is_valid_remote_reference, is_valid_local_reference, is_valid_markdown_reference
from refcheck.utils import (
    get_markdown_files_from_args,
    setup_arg_parser,
    print_green_background,
    print_red_background,
    print_red,
    print_green,
)


def main() -> bool:
    parser = setup_arg_parser()
    args = parser.parse_args()

    # Check if the user has provided any files or directories
    if not args.files and not args.directories:
        parser.print_help()
        return False

    no_color = args.no_color  # Get the no-color argument

    # Retrieve all markdown files specified by the user
    markdown_files = get_markdown_files_from_args(args.files, args.directories, args.exclude)
    if not markdown_files:
        print("[!] No Markdown files specified or found.")
        return False
    else:
        print(f"[+] {len(markdown_files)} Markdown files to check.")
        for file in markdown_files:
            print(f"- {file}")

    broken_references = []  # Collect broken references with line numbers

    for file in markdown_files:
        print(f"\n[+] Checking {file}...")
        base_path = os.path.dirname(file)
        references = parse_markdown_file(file)

        # Combine remote references
        remote_refs = (
            references["http_links"] + references["inline_links"] + references["raw_links"] + references["html_links"]
        )
        # Combine local references
        local_refs = references["file_refs"] + references["html_images"]

        if not remote_refs and not local_refs:
            print("-> No references found.")
            continue

        # Validate remote references
        for url, line_num in remote_refs:
            if is_valid_remote_reference(url):
                print(f"{file}:{line_num}: {url} - {print_green_background('OK', no_color)}")
            else:
                print(f"{file}:{line_num}: {url} - {print_red_background('BROKEN', no_color)}")
                broken_references.append((file, url, line_num))

        # Validate local references
        for ref, line_num in local_refs:
            if (".md" in ref and is_valid_markdown_reference(ref, base_path)) or is_valid_local_reference(
                ref, base_path
            ):
                print(f"{file}:{line_num}: {ref} - {print_green_background('OK', no_color)}")
            else:
                print(f"{file}:{line_num}: {ref} - {print_red_background('BROKEN', no_color)}")
                broken_references.append((file, ref, line_num))

    print("\nReference check complete.")

    # Summary of broken references
    print("\n============================|Summary|=============================")
    if broken_references:
        print(print_red(f"[!] {len(broken_references)} broken references found:", no_color))

        # Sort broken references by line number
        broken_references = sorted(broken_references, key=lambda x: (x[0], x[2]))

        for file, ref, line_num in broken_references:
            # Format output for easy navigation in VSCode
            print(f"{file}:{line_num}: {ref}")
    else:
        print(print_green("\U0001F389 No broken references.", no_color))
    print("==================================================================")

    # Return bool for exit code
    if broken_references:
        return False
    else:
        return True


if __name__ == "__main__":
    if main():
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
