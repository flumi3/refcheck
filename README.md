# RefCheck

RefCheck is a simple tool for finding broken references and links in Markdown
files.

```text
usage: refcheck [OPTIONS] [PATH ...]

positional arguments:
  PATH                  Markdown files or directories to check

options:
  -h, --help            show this help message and exit
  -e, --exclude [ ...]  Files or directories to exclude
  -cm, --check-remote   Check remote references (HTTP/HTTPS links)
  -n, --no-color        Turn off colored output
  -v, --verbose         Enable verbose output
```

> :memo: **Note**: RefCheck is still in its early development. If you encounter any issues or have suggestions, please
> feel free to open an issue or pull request.

## Installation

RefCheck is available on PyPI:

```bash
pip install refcheck
```

## Examples

```text
$ refcheck README.md

[+] 1 Markdown files to check.
- README.md

[+] FILE: README.md...
README.md:3: #introduction - OK
README.md:5: #installation - OK
README.md:6: #getting-started - OK

Reference check complete.

============================| Summary |=============================
🎉 No broken references.
====================================================================
```

```text
$ refcheck . --check-remote

[+] Searching for markdown files in C:\Users\flumi3\github\refcheck ...

[+] 2 Markdown files to check.
- tests\sample_markdown.md
- docs\Understanding-Markdown-References.md

[+] FILE: tests\sample_markdown.md...
tests\sample_markdown.md:39: /img/image.png - BROKEN
tests\sample_markdown.md:52: https://www.openai.com/logo.png - BROKEN

[+] FILE: docs\Understanding-Markdown-References.md...
docs\Understanding-Markdown-References.md:42: #local-file-references - OK

Reference check complete.

============================| Summary |=============================
[!] 2 broken references found:
tests\sample_markdown.md:39: /img/image.png
tests\sample_markdown.md:52: https://www.openai.com/logo.png
====================================================================
```

## Features

- Find and check various reference patterns in markdown files
- Highlight broken references
- Validate absolute and relative file paths to any file type
- Support for checking remote references, such as \[Google\]\(https://www.google.com)
- User friendly CLI
- Easy CI pipeline integration
