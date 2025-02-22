import pytest
from unittest.mock import mock_open, patch
from refcheck.validators import _header_exists  # No need to import _normalize_header

@pytest.mark.parametrize(
    "file_content, header, expected",
    [
        ("# Title\n## Section-1\n### Sub_section", "section-1", True),  # Header exists, normalized
        ("# Title\n## Section_One\n### Subsection", "section one", True),  # Underscore replaced by space
        ("# Header with (special)! chars?", "header-with-special-chars", True),  # Special characters removed
        ("# Title\n## Section 1\n### Subsection", "section_2", False),  # Wrong header
        ("", "Title", False),  # Empty file
        ("# Title\n## Another One", "another-one", True),  # Normalized match with dashes
        ("# Title\nSome random text", "some-random-text", False),  # No actual header match
    ]
)
@patch("refcheck.validators.open", new_callable=mock_open)
def test_header_exists(mock_file, file_content, header, expected):
    """Test if headers are correctly identified after normalization."""
    
    # Arrange
    mock_file.return_value.read.return_value = file_content

    # Act
    result = _header_exists("fake_path.md", header)

    # Assert
    assert result == expected, f"Expected {expected} but got {result} for header: {header}"

@patch("refcheck.validators.open", side_effect=FileNotFoundError)
@patch("refcheck.validators.logger.error")  # Mock logger to prevent actual logging
def test_header_exists_file_not_found(mock_logger, mock_file):
    """Test that _header_exists handles missing files correctly."""
    
    # Act
    result = _header_exists("missing.md", "Header")

    # Assert
    assert result is False
    mock_logger.assert_called_once_with("File not found: missing.md")
