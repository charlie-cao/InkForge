"""
InkForge - AI-powered high-quality blog content generator for global creators.

InkForge is an open-source CLI tool that helps content creators generate
high-quality, engaging blog posts tailored for different countries, platforms,
and industries using AI technology.

Key Features:
- Multi-country and multi-platform content adaptation
- Industry-specific content generation
- Humanization and engagement optimization
- Interactive CLI interface
- Extensible template system
"""

__version__ = "0.1.0"
__author__ = "InkForge Contributors"
__email__ = "contributors@inkforge.dev"
__license__ = "MIT"

from .core.generator import ContentGenerator
from .core.config import Config
from .models.content import ContentRequest, ContentResponse

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "ContentGenerator",
    "Config",
    "ContentRequest",
    "ContentResponse",
]
