import re
import argparse
import logging
from re import Pattern, Match
from dataclasses import dataclass

logger = logging.getLogger()

CODE_BLOCK_PATTERN = re.compile(r"```(?P<content>[\s\S]*?)```")

# Basic Markdown references
BASIC_REFERENCE_PATTERN = re.compile(r"!*\[(?P<text>.+)\]\((?P<link>.+)\)")  # []() and ![]()
BASIC_IMAGE_PATTERN = re.compile(r"!\[(?P<text>[^(){}\[\]]+)\]\((?P<link>[^(){}\[\]]+)\)")  # ![]()

# Inline Links - <http://example.com>
INLINE_LINK_PATTERN = re.compile(r"<(?P<link>.+)>")

RAW_LINK_PATTERN = re.compile(r"(^| )(?:(https?://\S+))")  # all links that are surrounded by nothing or spaces
HTML_LINK_PATTERN = re.compile(r"<a\s+(?:[^>]*?\s+)?href=([\"\'])(.*?)\1")  # <a href="http://example.com">

# Local File References - scripts, markdown files, and local images
HTML_IMAGE_PATTERN = re.compile(r"<img\s+(?:[^>]*?\s+)?src=([\"\'])(.*?)\1")  # <img src="image.png">


@dataclass
class Reference:
    """Data class to store reference information.

    Attributes:
        file_path: Path to the file where the reference was found.
        line_number: Line number where the reference was found.
        syntax: Syntax of the reference, e.g. `[text](link)`.
        link: The link part of the reference, e.g. `link` in `[text](link)`.
        is_remote: Whether the reference is a remote reference.
    """

    file_path: str
    line_number: int
    syntax: str
    link: str
    is_remote: bool


@dataclass
class ReferenceMatch:
    line_number: int
    match: Match


class MarkdownParser:

    def parse_markdown_file(self, file_path: str) -> dict[str, list[Reference]]:
        """Parse a markdown file to extract references.

        Args:
            file_path: Path to the markdown file.

        Returns:
            A dictionary containing lists of references found in the markdown file.
        """
        logger.info(f"Parsing markdown file: '{file_path}' ...")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
            return {}
        except IOError as e:
            print(f"Error: An I/O error occurred while reading the file {file_path}: {e}")
            return {}

        # Get all code blocks, such as ```python ... ```, or ```text``` for ensuring that found references are not part
        # of code blocks.
        logger.info("Extracting code blocks ...")
        code_blocks = self._find_matches_with_line_numbers(CODE_BLOCK_PATTERN, content)
        logger.info(f"Found {len(code_blocks)} code blocks.")

        # Get all references that look like this: [text](reference)
        logger.info("Extracting basic references ...")
        basic_references = self._find_matches_with_line_numbers(BASIC_REFERENCE_PATTERN, content)
        basic_references = [ref for ref in basic_references if not ref.match[0].startswith("!")]
        logger.info(f"Found {len(basic_references)} basic references.")
        basic_references = self._drop_code_block_references(basic_references, code_blocks)
        basic_references = self._process_basic_references(file_path, basic_references)

        # Get all image references that look like this: ![text](reference)
        logger.info("Extracting basic images ...")
        basic_images = self._find_matches_with_line_numbers(BASIC_IMAGE_PATTERN, content)
        logger.info(f"Found {len(basic_images)} basic images.")
        basic_images = self._drop_code_block_references(basic_images, code_blocks)
        basic_images = self._process_basic_references(file_path, basic_images)

        logger.info("Extracting inline links ...")
        inline_links = self._find_matches_with_line_numbers(INLINE_LINK_PATTERN, content)
        logger.info(f"Found {len(inline_links)} inline links.")
        inline_links = self._drop_code_block_references(inline_links, code_blocks)
        inline_links = self._process_basic_references(file_path, inline_links)

        return {
            "basic_references": basic_references,
            "basic_images": basic_images,
            "inline_links": inline_links,
        }

    def _drop_code_block_references(
        self, references: list[ReferenceMatch], code_blocks: list[ReferenceMatch]
    ) -> list[ReferenceMatch]:
        """Drop references that are part of code blocks."""
        logger.info("Dropping references that are part of code blocks ...")
        for ref in references:
            for code_block in code_blocks:
                logger.debug(ref.match.group(0))
                logger.debug(code_block.match.group(1))

                if ref.match.group(0) in code_block.match.group(1):
                    logger.info(f"Dropping reference: {ref.match.group(0)}")
                    references.remove(ref)
                    break
        return references

    def _is_remote_reference(self, link: str) -> bool:
        """Check if a link is a remote reference."""
        protocol_pattern = re.compile(
            r"^([a-zA-Z][a-zA-Z\d+\-.]*):.*"
        )  # matches anything that looks like a `protocol:`
        return bool(protocol_pattern.match(link))

    def _process_basic_references(self, file_path: str, matches: list[ReferenceMatch]) -> list[Reference]:
        """Process basic references."""
        references: list[Reference] = []
        for match in matches:
            link = match.match.group("link")
            reference = Reference(
                file_path=file_path,
                line_number=match.line_number,
                syntax=match.match.group(0),
                link=link,
                is_remote=self._is_remote_reference(link),
            )
            logger.info(reference.__repr__())
            references.append(reference)
        return references

    def _process_inline_links(self, file_path: str, matches: list[ReferenceMatch]) -> list[Reference]:
        # TODO: implement.
        # docs\Understanding-Markdown-References.md:49: <a href="https://www.wikipedia.org">Wikipedia</a>
        # docs\Understanding-Markdown-References.md:50: <a href='https://www.github.com'>GitHub</a>
        # docs\Understanding-Markdown-References.md:56: <img src="https://www.openai.com/logo.png" alt="OpenAI Logo">
        # docs\Understanding-Markdown-References.md:57: <img src="/assets/img.png" alt="Absolute Path Image">
        # docs\Understanding-Markdown-References.md:58: <img src="image.png" alt="Relative Path Image">
        pass

    def _find_matches_with_line_numbers(self, pattern: Pattern[str], text: str) -> list[ReferenceMatch]:
        """Find regex matches along with their line numbers."""
        matches_with_line_numbers = []
        for match in re.finditer(pattern, text):
            start_pos = match.start(0)
            line_number = text.count("\n", 0, start_pos) + 1
            matches_with_line_numbers.append(ReferenceMatch(line_number=line_number, match=match))
        return matches_with_line_numbers


# ============================== ARGUMENT PARSER ===============================


class CustomFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            (metavar,) = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    # parts.append('%s %s' % (option_string, args_string))
                    parts.append("%s" % option_string)
                parts[-1] += " %s" % args_string
            return ", ".join(parts)


def init_arg_parser():
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="refcheck", usage="refcheck [OPTIONS] [PATH ...]", formatter_class=CustomFormatter
    )
    parser.add_argument(
        "paths",
        metavar="PATH",
        type=str,
        nargs="*",
        help="Markdown files or directories to check",
    )
    parser.add_argument(
        "-e", "--exclude", metavar="", type=str, nargs="*", default=[], help="Files or directories to exclude"
    )
    parser.add_argument(
        "-cm", "--check-remote", action="store_true", help="Check remote references (HTTP/HTTPS links)"
    )
    parser.add_argument("-n", "--no-color", action="store_true", help="Turn off colored output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    return parser
