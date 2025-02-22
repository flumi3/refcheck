import pytest
from unittest.mock import patch
from refcheck.validators import is_valid_markdown_reference, Reference

@pytest.mark.parametrize(
    "link, file_path, file_exists_return, header_exists_return, expected",
    [
        ("#existing-header", "doc.md", True, True, True),  # Valid in-document header
        ("#missing-header", "doc.md", True, False, False),  # Missing header in the same document
        ("other.md#existing-header", "doc.md", True, True, True),  # Valid reference to another file's header
        ("other.md#missing-header", "doc.md", True, False, False),  # Missing header in another file
        ("missing.md#some-header", "doc.md", False, False, False),  # File does not exist
        ("valid.md", "doc.md", True, None, True),  # Valid Markdown file (no header reference)
        ("missing.md", "doc.md", False, None, False),  # Missing Markdown file
    ]
)
@patch("refcheck.validators.file_exists")
@patch("refcheck.validators._header_exists")
def test_is_valid_markdown_reference(
    mock_header_exists, mock_file_exists, link, file_path, file_exists_return, header_exists_return, expected
):
    """Test is_valid_markdown_reference for valid and invalid markdown section references."""
    
    # Arrange
    ref = Reference(
        file_path=file_path,
        line_number=10,  # Arbitrary, not used in the function
        syntax=f"[Example]({link})",
        link=link,
        is_remote=False  # Ensuring only local references are tested
    )
    
    mock_file_exists.return_value = file_exists_return
    mock_header_exists.return_value = header_exists_return if header_exists_return is not None else False

    # Act
    result = is_valid_markdown_reference(ref)

    # Assert
    assert result == expected, f"Expected {expected} but got {result} for link: {link}"
