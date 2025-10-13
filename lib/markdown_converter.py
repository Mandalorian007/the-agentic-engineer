"""Markdown to HTML conversion with syntax highlighting"""

from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from typing import Dict, Any
import re


class MarkdownConverter:
    """Convert markdown to HTML with syntax highlighting"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize markdown converter

        Args:
            config: Markdown configuration (extensions, highlighting style)
        """
        self.config = config

        # Initialize markdown-it with plugins
        self.md = (
            MarkdownIt('commonmark', {'html': True})
            .use(front_matter_plugin)
            .use(tasklists_plugin)
            .enable('table')
            .enable('strikethrough')
        )

        # Get syntax highlighting config
        syntax_config = config.get('syntax_highlighting', {})
        self.highlight_style = syntax_config.get('style', 'monokai')
        self.show_line_numbers = syntax_config.get('line_numbers', True)

    def convert(self, markdown_body: str) -> str:
        """
        Convert markdown to HTML

        Args:
            markdown_body: Markdown content (without frontmatter)

        Returns:
            HTML string
        """
        # First pass: convert markdown to HTML
        html = self.md.render(markdown_body)

        # Second pass: syntax highlight code blocks
        html = self._highlight_code_blocks(html)

        return html

    def _highlight_code_blocks(self, html: str) -> str:
        """
        Find and syntax-highlight code blocks in HTML

        Args:
            html: HTML with <code> blocks

        Returns:
            HTML with syntax-highlighted code blocks
        """
        # Pattern: <pre><code class="language-python">...</code></pre>
        # Only match code blocks inside <pre> tags, not inline <code>
        def replace_code(match):
            language = match.group(1) or ''
            code = match.group(2)

            # Unescape HTML entities in code
            code = (code
                    .replace('&lt;', '<')
                    .replace('&gt;', '>')
                    .replace('&amp;', '&')
                    .replace('&quot;', '"'))

            return self._highlight_code(code, language)

        # Match code blocks inside <pre> tags only (not inline code)
        pattern = r'<pre><code(?:\s+class="language-([^"]*)")?>(.*?)</code></pre>'
        return re.sub(pattern, replace_code, html, flags=re.DOTALL)

    def _highlight_code(self, code: str, language: str = '') -> str:
        """
        Syntax highlight a code block

        Args:
            code: Code to highlight
            language: Language identifier (python, javascript, etc.)

        Returns:
            HTML with syntax highlighting (wrapped in <pre><code>)
        """
        try:
            # Get lexer by language name
            if language:
                lexer = get_lexer_by_name(language, stripall=True)
            else:
                # Try to guess language
                lexer = guess_lexer(code)

            # Create formatter with inline styles (Blogger strips <style> tags)
            formatter = HtmlFormatter(
                style=self.highlight_style,
                linenos=False,  # Disable line numbers
                noclasses=True,  # Use inline styles instead of CSS classes
                wrapcode=True,
                nowrap=False  # Keep the <pre> wrapper
            )

            # Highlight and return (Pygments adds <div class="highlight"><pre>...)
            highlighted = highlight(code, lexer, formatter)
            return highlighted

        except ClassNotFound:
            # Language not found, return plain code block
            return f'<pre><code>{self._escape_html(code)}</code></pre>'

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))

    def get_css(self) -> str:
        """
        Get CSS for syntax highlighting

        Returns:
            CSS string for the configured style
        """
        formatter = HtmlFormatter(style=self.highlight_style)
        return formatter.get_style_defs('.highlight')


def create_converter(config: Dict[str, Any]) -> MarkdownConverter:
    """
    Factory function to create markdown converter

    Args:
        config: Full configuration dict (with markdown settings)

    Returns:
        Configured MarkdownConverter instance
    """
    from .config import get_markdown_config
    markdown_config = get_markdown_config(config)
    return MarkdownConverter(markdown_config)
