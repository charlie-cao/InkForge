"""Output formatters for InkForge."""

import json
import html
import re
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from ..models.content import ContentResponse, OutputFormat


class OutputFormatter:
    """Base class for output formatters."""
    
    def format(self, response: ContentResponse, **kwargs) -> str:
        """Format content response."""
        raise NotImplementedError
    
    def get_file_extension(self) -> str:
        """Get file extension for this format."""
        raise NotImplementedError


class MarkdownFormatter(OutputFormatter):
    """Markdown output formatter."""
    
    def format(self, response: ContentResponse, **kwargs) -> str:
        """Format content as Markdown."""
        output = []
        
        # Title
        output.append(f"# {response.title}")
        output.append("")
        
        # Metadata
        if kwargs.get("include_metadata", True):
            output.append("---")
            output.append(f"**Word Count:** {response.word_count}")
            output.append(f"**Reading Time:** {response.estimated_read_time} minutes")
            
            if response.tags:
                output.append(f"**Tags:** {', '.join(response.tags)}")
            
            generation_time = response.metadata.get("generation_time", "")
            if generation_time:
                output.append(f"**Generated:** {generation_time}")
            
            output.append("---")
            output.append("")
        
        # Main content
        output.append(response.content)
        output.append("")
        
        # Engagement tips
        if response.engagement_tips and kwargs.get("include_tips", True):
            output.append("## 💡 Engagement Tips")
            output.append("")
            for tip in response.engagement_tips:
                output.append(f"- {tip}")
            output.append("")
        
        # Platform-specific notes
        if response.platform_specific_notes and kwargs.get("include_notes", True):
            output.append("## 📝 Platform Notes")
            output.append("")
            for note in response.platform_specific_notes:
                output.append(f"- {note}")
            output.append("")
        
        return "\n".join(output)
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".md"


class HTMLFormatter(OutputFormatter):
    """HTML output formatter."""
    
    def format(self, response: ContentResponse, **kwargs) -> str:
        """Format content as HTML."""
        template = kwargs.get("template", "default")
        
        if template == "minimal":
            return self._format_minimal_html(response, **kwargs)
        else:
            return self._format_full_html(response, **kwargs)
    
    def _format_full_html(self, response: ContentResponse, **kwargs) -> str:
        """Format as full HTML document."""
        css_style = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #34495e;
                margin-top: 30px;
            }
            .metadata {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #3498db;
            }
            .tips, .notes {
                background: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #ffc107;
            }
            .tips ul, .notes ul {
                margin: 0;
                padding-left: 20px;
            }
            .content {
                margin: 30px 0;
            }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #666;
                font-size: 0.9em;
            }
        </style>
        """
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(response.title)}</title>
    {css_style}
</head>
<body>
    <h1>{html.escape(response.title)}</h1>
"""
        
        # Metadata
        if kwargs.get("include_metadata", True):
            html_content += f"""
    <div class="metadata">
        <strong>Word Count:</strong> {response.word_count}<br>
        <strong>Reading Time:</strong> {response.estimated_read_time} minutes<br>
"""
            if response.tags:
                tags_html = ", ".join(html.escape(tag) for tag in response.tags)
                html_content += f"        <strong>Tags:</strong> {tags_html}<br>\n"
            
            generation_time = response.metadata.get("generation_time", "")
            if generation_time:
                html_content += f"        <strong>Generated:</strong> {generation_time}<br>\n"
            
            html_content += "    </div>\n"
        
        # Main content
        content_html = self._markdown_to_html(response.content)
        html_content += f"""
    <div class="content">
        {content_html}
    </div>
"""
        
        # Engagement tips
        if response.engagement_tips and kwargs.get("include_tips", True):
            html_content += """
    <div class="tips">
        <h2>💡 Engagement Tips</h2>
        <ul>
"""
            for tip in response.engagement_tips:
                html_content += f"            <li>{html.escape(tip)}</li>\n"
            html_content += "        </ul>\n    </div>\n"
        
        # Platform notes
        if response.platform_specific_notes and kwargs.get("include_notes", True):
            html_content += """
    <div class="notes">
        <h2>📝 Platform Notes</h2>
        <ul>
"""
            for note in response.platform_specific_notes:
                html_content += f"            <li>{html.escape(note)}</li>\n"
            html_content += "        </ul>\n    </div>\n"
        
        # Footer
        html_content += f"""
    <div class="footer">
        Generated by InkForge - AI-powered content creation tool
    </div>
</body>
</html>"""
        
        return html_content
    
    def _format_minimal_html(self, response: ContentResponse, **kwargs) -> str:
        """Format as minimal HTML (content only)."""
        html_content = f"<h1>{html.escape(response.title)}</h1>\n\n"
        html_content += self._markdown_to_html(response.content)
        return html_content
    
    def _markdown_to_html(self, content: str) -> str:
        """Convert basic Markdown to HTML."""
        # This is a simple converter - for production, use a proper Markdown library
        html_content = html.escape(content)
        
        # Headers
        html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        
        # Bold and italic
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
        
        # Links
        html_content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html_content)
        
        # Paragraphs
        paragraphs = html_content.split('\n\n')
        html_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                if not para.startswith('<h') and not para.startswith('<ul') and not para.startswith('<ol'):
                    para = f"<p>{para}</p>"
                html_paragraphs.append(para)
        
        return '\n\n'.join(html_paragraphs)
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".html"


class JSONFormatter(OutputFormatter):
    """JSON output formatter."""
    
    def format(self, response: ContentResponse, **kwargs) -> str:
        """Format content as JSON."""
        data = response.dict()
        
        # Add formatting options
        if kwargs.get("pretty", True):
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, ensure_ascii=False)
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".json"


class PlainTextFormatter(OutputFormatter):
    """Plain text output formatter."""
    
    def format(self, response: ContentResponse, **kwargs) -> str:
        """Format content as plain text."""
        output = []
        
        # Title
        output.append(response.title.upper())
        output.append("=" * len(response.title))
        output.append("")
        
        # Metadata
        if kwargs.get("include_metadata", True):
            output.append(f"Word Count: {response.word_count}")
            output.append(f"Reading Time: {response.estimated_read_time} minutes")
            
            if response.tags:
                output.append(f"Tags: {', '.join(response.tags)}")
            
            output.append("")
            output.append("-" * 50)
            output.append("")
        
        # Main content (strip Markdown formatting)
        clean_content = self._strip_markdown(response.content)
        output.append(clean_content)
        output.append("")
        
        # Tips and notes
        if response.engagement_tips and kwargs.get("include_tips", True):
            output.append("ENGAGEMENT TIPS:")
            output.append("-" * 20)
            for i, tip in enumerate(response.engagement_tips, 1):
                output.append(f"{i}. {tip}")
            output.append("")
        
        if response.platform_specific_notes and kwargs.get("include_notes", True):
            output.append("PLATFORM NOTES:")
            output.append("-" * 20)
            for i, note in enumerate(response.platform_specific_notes, 1):
                output.append(f"{i}. {note}")
            output.append("")
        
        return "\n".join(output)
    
    def _strip_markdown(self, content: str) -> str:
        """Strip Markdown formatting."""
        import re
        
        # Remove headers
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
        
        # Remove bold/italic
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)
        content = re.sub(r'\*(.+?)\*', r'\1', content)
        
        # Remove links
        content = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', content)
        
        # Remove other formatting
        content = re.sub(r'`(.+?)`', r'\1', content)
        content = re.sub(r'^>\s+', '', content, flags=re.MULTILINE)
        
        return content
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".txt"


class FormatterFactory:
    """Factory for creating output formatters."""
    
    _formatters = {
        OutputFormat.MARKDOWN: MarkdownFormatter,
        OutputFormat.HTML: HTMLFormatter,
        OutputFormat.JSON: JSONFormatter,
        OutputFormat.PLAIN: PlainTextFormatter,
    }
    
    @classmethod
    def get_formatter(cls, format_type: OutputFormat) -> OutputFormatter:
        """Get formatter for the specified format."""
        formatter_class = cls._formatters.get(format_type)
        if formatter_class is None:
            raise ValueError(f"Unsupported output format: {format_type}")
        
        return formatter_class()
    
    @classmethod
    def get_supported_formats(cls) -> list:
        """Get list of supported formats."""
        return list(cls._formatters.keys())


def format_content(
    response: ContentResponse,
    format_type: OutputFormat,
    output_file: Optional[Path] = None,
    **kwargs
) -> str:
    """Format content and optionally save to file."""
    formatter = FormatterFactory.get_formatter(format_type)
    formatted_content = formatter.format(response, **kwargs)
    
    if output_file:
        # Ensure the file has the correct extension
        if not output_file.suffix:
            output_file = output_file.with_suffix(formatter.get_file_extension())
        
        # Create directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        output_file.write_text(formatted_content, encoding='utf-8')
    
    return formatted_content
