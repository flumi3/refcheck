# tests/test_parsers.py
import pytest
from refcheck.parsers import (
    parse_markdown_file,
    find_matches_with_line_numbers,
    HTTP_LINK_PATTERN,
    INLINE_LINK_PATTERN,
    RAW_LINK_PATTERN,
    HTML_LINK_PATTERN,
    FILE_PATTERN,
    HTML_IMAGE_PATTERN,
)


@pytest.fixture
def sample_markdown():
    with open("tests/sample_markdown.md", "r", encoding="utf-8") as file:
        return file.read()


def test_http_links(sample_markdown):
    http_links = find_matches_with_line_numbers(HTTP_LINK_PATTERN, sample_markdown, group=2)
    expected = [
        ("https://www.openai.com", 3),
        ("http://www.openai.com", 4),
        ("https://www.google.com", 7),
        ("http://example.com", 8),
        ("http://anotherexample.com", 11),
        ("http://example-link-in-markdown.com", 16),
    ]
    assert http_links == expected


def test_inline_links(sample_markdown):
    inline_links = find_matches_with_line_numbers(INLINE_LINK_PATTERN, sample_markdown, group=1)
    expected = [("http://example.com", 21), ("https://example.com", 22), ("http://example.com", 24)]
    assert inline_links == expected


def test_raw_links(sample_markdown):
    raw_links = find_matches_with_line_numbers(RAW_LINK_PATTERN, sample_markdown, group=2)
    expected = [
        ("http://example.com", 28),
        ("http://example.com", 29),
        ("http://example.com", 30),
    ]
    assert raw_links == expected


def test_html_links(sample_markdown):
    html_links = find_matches_with_line_numbers(HTML_LINK_PATTERN, sample_markdown, group=2)
    expected = [("http://example.com", 34), ("http://example.com", 35)]
    assert html_links == expected


def test_file_links(sample_markdown):
    file_refs = find_matches_with_line_numbers(FILE_PATTERN, sample_markdown, group=2)
    expected = [
        ("/img/image.png", 39),
        ("img.png", 40),
        ("src/main.py", 42),
        ("docs/user_guide.md", 43),
        ("/project/docs/good-doc.md", 44),
        ("other-directory/README.md#installation-instructions", 46),
        ("/path/to/README.md#getting-started", 47),
        ("#markdown-links-with-headers", 48),
    ]
    assert file_refs == expected


def test_html_images(sample_markdown):
    html_images = find_matches_with_line_numbers(HTML_IMAGE_PATTERN, sample_markdown, group=2)
    expected = [("https://www.openai.com/logo.png", 52), ("/assets/img.png", 53), ("image.png", 54)]
    assert html_images == expected


def test_parse_markdown_file(monkeypatch, tmp_path):
    # Create a temporary markdown file with the sample markdown content
    test_markdown_path = tmp_path / "test_readme.md"
    test_markdown_content = """# Understanding Markdown References
- [OpenAI HTTPS](https://www.openai.com)
    """

    test_markdown_path.write_text(test_markdown_content)

    # Parse the created markdown file
    parsed_references = parse_markdown_file(test_markdown_path)

    assert "http_links" in parsed_references
    assert parsed_references["http_links"] == [("https://www.openai.com", 2)]


if __name__ == "__main__":
    pytest.main()
