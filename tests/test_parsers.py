import pytest
from refcheck.parsers import (
    parse_markdown_file,
    _find_matches_with_line_numbers,
    init_arg_parser,
    HTTP_LINK_PATTERN,
    INLINE_LINK_PATTERN,
    RAW_LINK_PATTERN,
    HTML_LINK_PATTERN,
    FILE_PATTERN,
    HTML_IMAGE_PATTERN,
)


# Sample markdown content for testing
@pytest.fixture
def sample_markdown():
    with open("tests/sample_markdown.md", "r", encoding="utf-8") as file:
        return file.read()


# Tests for HTTP links
def test_http_links(sample_markdown):
    http_links = _find_matches_with_line_numbers(HTTP_LINK_PATTERN, sample_markdown, group=2)
    expected = [
        ("https://www.openai.com", 3),
        ("http://www.openai.com", 4),
        ("https://www.google.com", 7),
        ("http://example.com", 8),
        ("http://anotherexample.com", 11),
        ("http://example-link-in-markdown.com", 16),
    ]
    assert http_links == expected


# Tests for inline links
def test_inline_links(sample_markdown):
    inline_links = _find_matches_with_line_numbers(INLINE_LINK_PATTERN, sample_markdown, group=1)
    expected = [("http://example.com", 21), ("https://example.com", 22), ("http://example.com", 24)]
    assert inline_links == expected


# Tests for raw links
def test_raw_links(sample_markdown):
    raw_links = _find_matches_with_line_numbers(RAW_LINK_PATTERN, sample_markdown, group=2)
    expected = [
        ("http://example.com", 28),
        ("http://example.com", 29),
        ("http://example.com", 30),
    ]
    assert raw_links == expected


# Tests for HTML links
def test_html_links(sample_markdown):
    html_links = _find_matches_with_line_numbers(HTML_LINK_PATTERN, sample_markdown, group=2)
    expected = [("http://example.com", 34), ("http://example.com", 35)]
    assert html_links == expected


# Tests for file references
def test_file_links(sample_markdown):
    file_refs = _find_matches_with_line_numbers(FILE_PATTERN, sample_markdown, group=2)
    expected = [
        ("/img/image.png", 39),
        ("img.png", 40),
        ("src/main.py", 42),
        ("docs/user_guide.md", 43),
        ("/project/docs/good-doc.md", 44),
        ("other-directory/README.md#installation-instructions", 46),
        ("/path/to/README.md#getting-started", 47),
        ("#file-links", 48),
    ]
    assert file_refs == expected


# Tests for HTML images
def test_html_images(sample_markdown):
    html_images = _find_matches_with_line_numbers(HTML_IMAGE_PATTERN, sample_markdown, group=2)
    expected = [("https://www.openai.com/logo.png", 52), ("/assets/img.png", 53), ("image.png", 54)]
    assert html_images == expected


# Tests for parsing an entire markdown file
def test_parse_markdown_file(tmp_path):
    # Create a temporary markdown file with sample content
    test_markdown_path = tmp_path / "test_readme.md"
    test_markdown_content = """# Understanding Markdown References
- [OpenAI HTTPS](https://www.openai.com)
    """
    test_markdown_path.write_text(test_markdown_content)

    # Parse the created markdown file
    parsed_references = parse_markdown_file(test_markdown_path)

    assert "http_links" in parsed_references
    assert parsed_references["http_links"] == [("https://www.openai.com", 2)]


# Tests for setting up argument parser
def test_setup_arg_parser():
    parser = init_arg_parser()
    args = parser.parse_args(["file1.md", "file2.md", "dir1", "dir2", "-e", "exclude1", "exclude2", "-n"])
    assert args.paths == ["file1.md", "file2.md", "dir1", "dir2"]
    assert args.exclude == ["exclude1", "exclude2"]
    assert args.no_color is True


# Test no-links scenario
def test_no_links():
    empty_md = ""
    parsed_references = parse_markdown_file(empty_md)
    for key in parsed_references.keys():
        assert parsed_references[key] == []


def test_no_file():
    parsed_references = parse_markdown_file("non_existent_file.md")
    assert parsed_references == {}


# TODO: Test for malformed markdown content
def test_malformed_links():
    pass


# Test invalid argument parsing
def test_invalid_arg_parser():
    parser = init_arg_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--invalid-arg"])


# Parameterized tests for various link types
@pytest.mark.parametrize(
    "md_content, expected_refs",
    [
        # Remote links
        ("- [HTTPS Link](https://www.example.com)", {"http_links": [("https://www.example.com", 1)]}),
        ("- [HTTP Link](http://www.example.com)", {"http_links": [("http://www.example.com", 1)]}),
        (
            "> - [Remote Link in Callout](http://anotherexample.com)",
            {"http_links": [("http://anotherexample.com", 1)]},
        ),
        (
            "```markdown\n[Remote Link in Code Block](http://example-link-in-markdown.com)\n```",
            {"http_links": [("http://example-link-in-markdown.com", 2)]},
        ),
        ("- <http://example.com>", {"inline_links": [("http://example.com", 1)]}),
        ("- <https://example.com>", {"inline_links": [("https://example.com", 1)]}),
        ("- Direct link to resource: http://example.com", {"raw_links": [("http://example.com", 1)]}),
        ('- <a href="http://example.com">HTLM HTTP Link</a>', {"html_links": [("http://example.com", 1)]}),
        ("- <a href='https://example.com'>HTLM HTTPS Link</a>", {"html_links": [("https://example.com", 1)]}),
        # Local files
        ("- ![Absolute Image Path](/img/image.png)", {"file_refs": [("/img/image.png", 1)]}),
        ("- ![Relative Image Path](img.png)", {"file_refs": [("img.png", 1)]}),
        ("- [Relative File Path](src/main.py)", {"file_refs": [("src/main.py", 1)]}),
        ("- [Absolute File Path](/docs/user_guide.md)", {"file_refs": [("/docs/user_guide.md", 1)]}),
        (
            "- [Relative Reference to Header](good-doc.md#introduction)",
            {"file_refs": [("good-doc.md#introduction", 1)]},
        ),
        (
            "- [Absolute Reference to Header](/project/docs/good-doc.md#introduction)",
            {"file_refs": [("/project/docs/good-doc.md#introduction", 1)]},
        ),
        ("- [Reference to a header in the same file](#getting-started)", {"file_refs": [("#getting-started", 1)]}),
        (
            '- <img src="https://www.openai.com/logo.png" alt="OpenAI Logo">',
            {"html_images": [("https://www.openai.com/logo.png", 1)]},
        ),
        ('- <img src="/assets/img.png" alt="Absolute Path Image">', {"html_images": [("/assets/img.png", 1)]}),
        ('- <img src="image.png" alt="Relative Path Image">', {"html_images": [("image.png", 1)]}),
    ],
)
def test_various_links(md_content, expected_refs, tmp_path):
    test_markdown_path = tmp_path / "test_readme.md"
    test_markdown_path.write_text(md_content)
    parsed_references = parse_markdown_file(test_markdown_path)

    for key, expected in expected_refs.items():
        assert parsed_references[key] == expected


# Main execution
if __name__ == "__main__":
    pytest.main()
