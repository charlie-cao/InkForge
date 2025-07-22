"""Tests for InkForge output formatters."""

import json
import tempfile
from pathlib import Path

import pytest

from inkforge.models.content import ContentResponse, OutputFormat
from inkforge.utils.formatters import (
    MarkdownFormatter, HTMLFormatter, JSONFormatter, PlainTextFormatter,
    FormatterFactory, format_content
)


@pytest.fixture
def sample_response():
    """Create a sample ContentResponse for testing."""
    return ContentResponse(
        title="Test Blog Post",
        content="# Introduction\n\nThis is a **test** blog post with *emphasis* and [links](https://example.com).\n\n## Main Content\n\nHere's the main content with multiple paragraphs.\n\nThis is another paragraph.",
        word_count=25,
        estimated_read_time=1,
        tags=["test", "blog", "sample"],
        engagement_tips=["Ask questions", "Use emojis"],
        platform_specific_notes=["Optimize for Medium", "Use subheadings"],
        metadata={
            "generation_model": "test-model",
            "generation_time": "2024-01-01T12:00:00",
        }
    )


class TestMarkdownFormatter:
    """Test MarkdownFormatter."""
    
    def test_basic_formatting(self, sample_response):
        """Test basic Markdown formatting."""
        formatter = MarkdownFormatter()
        result = formatter.format(sample_response)
        
        assert "# Test Blog Post" in result
        assert "**Word Count:** 25" in result
        assert "**Reading Time:** 1 minutes" in result
        assert "**Tags:** test, blog, sample" in result
        assert "## 💡 Engagement Tips" in result
        assert "- Ask questions" in result
        assert "## 📝 Platform Notes" in result
        assert "- Optimize for Medium" in result
    
    def test_without_metadata(self, sample_response):
        """Test formatting without metadata."""
        formatter = MarkdownFormatter()
        result = formatter.format(sample_response, include_metadata=False)
        
        assert "# Test Blog Post" in result
        assert "**Word Count:**" not in result
        assert "---" not in result
    
    def test_without_tips(self, sample_response):
        """Test formatting without tips."""
        formatter = MarkdownFormatter()
        result = formatter.format(sample_response, include_tips=False)
        
        assert "## 💡 Engagement Tips" not in result
        assert "- Ask questions" not in result
    
    def test_file_extension(self):
        """Test file extension."""
        formatter = MarkdownFormatter()
        assert formatter.get_file_extension() == ".md"


class TestHTMLFormatter:
    """Test HTMLFormatter."""
    
    def test_full_html_formatting(self, sample_response):
        """Test full HTML formatting."""
        formatter = HTMLFormatter()
        result = formatter.format(sample_response)
        
        assert "<!DOCTYPE html>" in result
        assert "<title>Test Blog Post</title>" in result
        assert "<h1>Test Blog Post</h1>" in result
        assert "<div class=\"metadata\">" in result
        assert "<strong>Word Count:</strong> 25" in result
        assert "<div class=\"tips\">" in result
        assert "<div class=\"notes\">" in result
    
    def test_minimal_html_formatting(self, sample_response):
        """Test minimal HTML formatting."""
        formatter = HTMLFormatter()
        result = formatter.format(sample_response, template="minimal")
        
        assert "<!DOCTYPE html>" not in result
        assert "<h1>Test Blog Post</h1>" in result
        assert "<div class=\"metadata\">" not in result
    
    def test_markdown_to_html_conversion(self, sample_response):
        """Test Markdown to HTML conversion."""
        formatter = HTMLFormatter()
        result = formatter.format(sample_response)
        
        # Check that Markdown is converted to HTML
        assert "<h1>" in result or "<h2>" in result
        assert "<strong>" in result  # **bold** -> <strong>
        assert "<em>" in result     # *italic* -> <em>
        assert "<a href=" in result # [link](url) -> <a>
    
    def test_file_extension(self):
        """Test file extension."""
        formatter = HTMLFormatter()
        assert formatter.get_file_extension() == ".html"


class TestJSONFormatter:
    """Test JSONFormatter."""
    
    def test_json_formatting(self, sample_response):
        """Test JSON formatting."""
        formatter = JSONFormatter()
        result = formatter.format(sample_response)
        
        # Parse JSON to verify it's valid
        data = json.loads(result)
        
        assert data["title"] == "Test Blog Post"
        assert data["word_count"] == 25
        assert data["tags"] == ["test", "blog", "sample"]
        assert data["engagement_tips"] == ["Ask questions", "Use emojis"]
    
    def test_json_pretty_formatting(self, sample_response):
        """Test pretty JSON formatting."""
        formatter = JSONFormatter()
        result = formatter.format(sample_response, pretty=True)
        
        # Pretty formatting should have indentation
        assert "  " in result  # Indentation
        assert "\n" in result  # Line breaks
    
    def test_json_compact_formatting(self, sample_response):
        """Test compact JSON formatting."""
        formatter = JSONFormatter()
        result = formatter.format(sample_response, pretty=False)
        
        # Compact formatting should not have extra whitespace
        assert "  " not in result  # No indentation
        # Should still be valid JSON
        data = json.loads(result)
        assert data["title"] == "Test Blog Post"
    
    def test_file_extension(self):
        """Test file extension."""
        formatter = JSONFormatter()
        assert formatter.get_file_extension() == ".json"


class TestPlainTextFormatter:
    """Test PlainTextFormatter."""
    
    def test_plain_text_formatting(self, sample_response):
        """Test plain text formatting."""
        formatter = PlainTextFormatter()
        result = formatter.format(sample_response)
        
        assert "TEST BLOG POST" in result  # Title in uppercase
        assert "=" in result  # Title underline
        assert "Word Count: 25" in result
        assert "Reading Time: 1 minutes" in result
        assert "Tags: test, blog, sample" in result
        assert "ENGAGEMENT TIPS:" in result
        assert "1. Ask questions" in result
        assert "PLATFORM NOTES:" in result
        assert "1. Optimize for Medium" in result
    
    def test_markdown_stripping(self, sample_response):
        """Test Markdown formatting removal."""
        formatter = PlainTextFormatter()
        result = formatter.format(sample_response)
        
        # Markdown formatting should be stripped
        assert "**" not in result  # No bold markers
        assert "*" not in result   # No italic markers (except in bullet points)
        assert "[" not in result   # No link brackets
        assert "#" not in result   # No header markers
    
    def test_without_metadata(self, sample_response):
        """Test formatting without metadata."""
        formatter = PlainTextFormatter()
        result = formatter.format(sample_response, include_metadata=False)
        
        assert "Word Count:" not in result
        assert "Reading Time:" not in result
        assert "-" * 50 not in result
    
    def test_file_extension(self):
        """Test file extension."""
        formatter = PlainTextFormatter()
        assert formatter.get_file_extension() == ".txt"


class TestFormatterFactory:
    """Test FormatterFactory."""
    
    def test_get_markdown_formatter(self):
        """Test getting Markdown formatter."""
        formatter = FormatterFactory.get_formatter(OutputFormat.MARKDOWN)
        assert isinstance(formatter, MarkdownFormatter)
    
    def test_get_html_formatter(self):
        """Test getting HTML formatter."""
        formatter = FormatterFactory.get_formatter(OutputFormat.HTML)
        assert isinstance(formatter, HTMLFormatter)
    
    def test_get_json_formatter(self):
        """Test getting JSON formatter."""
        formatter = FormatterFactory.get_formatter(OutputFormat.JSON)
        assert isinstance(formatter, JSONFormatter)
    
    def test_get_plain_formatter(self):
        """Test getting plain text formatter."""
        formatter = FormatterFactory.get_formatter(OutputFormat.PLAIN)
        assert isinstance(formatter, PlainTextFormatter)
    
    def test_unsupported_format(self):
        """Test unsupported format."""
        with pytest.raises(ValueError, match="Unsupported output format"):
            FormatterFactory.get_formatter("unsupported")
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = FormatterFactory.get_supported_formats()
        
        assert OutputFormat.MARKDOWN in formats
        assert OutputFormat.HTML in formats
        assert OutputFormat.JSON in formats
        assert OutputFormat.PLAIN in formats
        assert len(formats) == 4


class TestFormatContent:
    """Test format_content function."""
    
    def test_format_content_markdown(self, sample_response):
        """Test formatting content as Markdown."""
        result = format_content(sample_response, OutputFormat.MARKDOWN)
        assert "# Test Blog Post" in result
    
    def test_format_content_with_file(self, sample_response):
        """Test formatting content and saving to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_output"
            
            result = format_content(
                sample_response,
                OutputFormat.MARKDOWN,
                output_file=output_file
            )
            
            # Check that file was created with correct extension
            expected_file = output_file.with_suffix(".md")
            assert expected_file.exists()
            
            # Check file content
            file_content = expected_file.read_text(encoding='utf-8')
            assert file_content == result
            assert "# Test Blog Post" in file_content
    
    def test_format_content_with_existing_extension(self, sample_response):
        """Test formatting with existing file extension."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_output.md"
            
            format_content(
                sample_response,
                OutputFormat.MARKDOWN,
                output_file=output_file
            )
            
            # Should use the existing extension
            assert output_file.exists()
            assert not (output_file.parent / "test_output.md.md").exists()
    
    def test_format_content_creates_directory(self, sample_response):
        """Test that format_content creates directories if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "subdir" / "test_output"
            
            format_content(
                sample_response,
                OutputFormat.JSON,
                output_file=output_file
            )
            
            expected_file = output_file.with_suffix(".json")
            assert expected_file.exists()
            assert expected_file.parent.exists()
