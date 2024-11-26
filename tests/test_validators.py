import pytest
from unittest.mock import patch, mock_open
from refcheck.validators import (
    is_valid_remote_reference,
    header_exists,
    normalize_header,
    is_valid_markdown_reference,
)


@patch("refcheck.validators.requests.head")
def test_is_valid_remote_reference(mock_requests_head):
    # Mock successful response
    mock_requests_head.return_value.status_code = 200
    assert is_valid_remote_reference("https://example.com")

    # Mock not found response
    mock_requests_head.return_value.status_code = 404
    assert not is_valid_remote_reference("https://example.com")

    # Mock exception
    mock_requests_head.side_effect = Exception()
    assert not is_valid_remote_reference("https://example.com")


def test_normalize_header():
    assert normalize_header("  Example Header  ") == "example-header"
    assert normalize_header("Special/Characters!") == "specialcharacters"
    assert normalize_header("") == ""
    assert normalize_header("A very long header with multiple parts!") == "a-very-long-header-with-multiple-parts"


@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data="# Header 1\n## Header 2\n### Example-Header")
def test_header_exists(mock_open, mock_file_exists):
    # Mock file exists
    mock_file_exists.return_value = True

    file_path = "/project/docs/user_guide.md"

    # Header exists
    assert header_exists(file_path, "Header 1")
    assert header_exists(file_path, "Header 2")
    assert header_exists(file_path, "Example-Header")

    # Header does not exist
    assert not header_exists(file_path, "Non-Existing Header")


@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data="# Header 1\n## Header 2\n### Example-Header")
def test_is_valid_markdown_reference(mock_open, mock_exists):
    base_path = "/project"

    # Mock file exists
    mock_exists.return_value = True

    # Valid file reference without header
    assert is_valid_markdown_reference("docs/user_guide.md", base_path)

    # Valid file reference with existing header
    assert is_valid_markdown_reference("docs/user_guide.md#header-1", base_path)
    assert is_valid_markdown_reference("docs/user_guide.md#header-2", base_path)
    assert is_valid_markdown_reference("docs/user_guide.md#example-header", base_path)

    # Valid file reference with non-existing header
    assert not is_valid_markdown_reference("docs/user_guide.md#non-existing-header", base_path)

    # Invalid file reference
    mock_exists.return_value = False
    assert not is_valid_markdown_reference("docs/non_existing_file.md", base_path)


if __name__ == "__main__":
    pytest.main()
