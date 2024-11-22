# TOC

- [RefCheck](#refcheck)
  - [Features](#features)
  - [Installation](#installation)
  - [Contributing](#contributing)

# RefCheck

RefCheck is a simple tool for validating markdown references and highlighting
any broken ones.

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

## Examples

```text
$ refcheck README.md

[+] 1 Markdown files to check.
- README.md

[+] Checking README.md...
README.md:3: #introduction - OK
README.md:5: #installation - OK
README.md:6: #getting-started - OK
README.md:24: https://www.github.com - OK

Reference check complete.

============================| Summary |=============================
🎉 No broken references.
====================================================================
```

```text
$ refcheck .

[+] Searching for markdown files in C:\Users\zoseflum\git\github\flumi3\refcheck ...
[+] 3 Markdown files to check.
- tests\sample_markdown.md
- docs\Understanding-Markdown-References.md
- README.md

[+] Checking tests\sample_markdown.md...
tests\sample_markdown.md:39: /img/image.png - BROKEN
tests\sample_markdown.md:40: img.png - BROKEN
tests\sample_markdown.md:52: https://www.openai.com/logo.png - BROKEN

[+] Checking docs\Understanding-Markdown-References.md...
docs\Understanding-Markdown-References.md:42: #local-file-references - OK


============================| Summary |=============================
[!] 21 broken references found:
tests\sample_markdown.md:39: /img/image.png
tests\sample_markdown.md:40: img.png
tests\sample_markdown.md:52: https://www.openai.com/logo.png
====================================================================
```


## Features

- Find and check references in markdown files
- Highlight broken references
- Validate absolute and relative file paths to any file type
- Support for checking remote references, such as \[Google\]\(https://www.google.com\)
- User friendly CLI
- Easy CI pipeline integration

## Installation

```bash
pip install refcheck
```

## Contributing

TODO
