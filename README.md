# 🔥 InkForge

**AI-powered high-quality blog content generator for global creators**

InkForge is an open-source CLI tool that helps content creators generate engaging, platform-optimized blog posts tailored for different countries, industries, and audiences using advanced AI technology.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

- 🌍 **Global Localization**: Optimized content for different countries and cultures
- 🏭 **Industry-Specific**: Tailored content for various industries (finance, health, tech, etc.)
- 📱 **Platform Optimization**: Adapted for Medium, Zhihu, Twitter, LinkedIn, and more
- 🤖 **AI-Powered**: Uses advanced language models via OpenRouter API
- 🎨 **Humanization**: Makes AI content feel natural and engaging
- 📊 **Engagement Optimization**: Built-in strategies to boost likes, shares, and comments
- 🔧 **Interactive CLI**: User-friendly command-line interface
- 📄 **Multiple Formats**: Export to Markdown, HTML, JSON, or plain text
- 💾 **Auto-Save**: Automatic saving in multiple formats with session management
- 📊 **Session Tracking**: Detailed logging and session history
- 🧪 **Quality Control**: Built-in content quality scoring and retry mechanisms

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/inkforge/inkforge.git
cd inkforge

# Install dependencies
pip install -e .

# Or install from PyPI (when available)
pip install inkforge
```

### Configuration

1. Get your OpenRouter API key from [OpenRouter](https://openrouter.ai/)
2. Set up your environment:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
OPENROUTER_API_KEY=your_api_key_here
```

### Basic Usage

```bash
# Generate a blog post
inkforge generate "The Future of AI in Healthcare"

# Specify target audience and platform
inkforge generate "投资理财入门指南" --country CN --platform zhihu --industry finance

# Interactive mode for step-by-step configuration
inkforge generate "Tech Trends 2024" --interactive

# Save to file with specific format
inkforge generate "Travel Tips" --format html --output travel-post.html

# Auto-save in multiple formats (default: md,html,json)
inkforge generate "Tech Guide" --save-formats "md,html,txt,json"

# Disable auto-save
inkforge generate "Quick Note" --no-auto-save
```

## 📖 Documentation

### Command Reference

#### Generate Content

```bash
inkforge generate [TOPIC] [OPTIONS]
```

**Options:**
- `--country, -co`: Target country (US, CN, JP, FR, DE, UK, KR, IN, BR, ES)
- `--industry, -i`: Target industry (general, finance, health, education, gaming, technology, lifestyle, business, travel, food)
- `--platform, -p`: Target platform (medium, zhihu, twitter, xiaohongshu, wechat, linkedin, substack, note, blog)
- `--tone, -t`: Content tone (professional, casual, entertaining, analytical, inspirational, neutral)
- `--goal, -g`: Content goal (engagement, conversion, shares, comments, followers, awareness)
- `--language, -l`: Target language (auto-detected from country if not specified)
- `--keywords, -k`: Comma-separated keywords to include
- `--length, -len`: Approximate word count (100-5000)
- `--format, -f`: Output format (markdown, html, json, plain)
- `--output, -o`: Output file path
- `--save-formats`: Comma-separated formats to auto-save (md,html,json,txt)
- `--auto-save/--no-auto-save`: Enable/disable auto-save (default: enabled)
- `--interactive, -int`: Interactive mode
- `--instructions`: Custom instructions for the AI

#### Configuration Management

```bash
# Show current configuration
inkforge config --show

# Set API key
inkforge config --set openrouter_api_key --value your_key_here

# Reset to defaults
inkforge config --reset

# View recent sessions
inkforge sessions --list

# Show session details
inkforge sessions --show 20241201_143022

# Clean old sessions
inkforge sessions --clean
```

### Examples

#### Basic Blog Post
```bash
inkforge generate "How to Start a Successful Blog in 2024"
```

#### Chinese Finance Content for Zhihu
```bash
inkforge generate "2024年投资策略分析" \
  --country CN \
  --industry finance \
  --platform zhihu \
  --tone analytical \
  --keywords "投资,理财,股市,基金"
```

#### Twitter Thread
```bash
inkforge generate "10 AI Tools Every Developer Should Know" \
  --platform twitter \
  --goal shares \
  --length 500
```

#### Professional LinkedIn Article
```bash
inkforge generate "The Future of Remote Work" \
  --platform linkedin \
  --tone professional \
  --industry business \
  --goal followers

## 💾 Auto-Save and Session Management

InkForge automatically saves all generated content with detailed session tracking:

### Auto-Save Features
- **Multiple Formats**: Save content in Markdown, HTML, JSON, and plain text simultaneously
- **Session Organization**: Each session gets a unique ID and directory
- **Detailed Logging**: Complete generation logs with timing, quality scores, and retry information
- **Metadata Tracking**: Full request parameters, AI responses, and processing details

### Session Structure
```
output/sessions/YYYYMMDD_HHMMSS/
├── session.log                 # Detailed session log
├── session_data.json          # Session metadata
├── gen_HHMMSS/                # Individual generation
│   ├── metadata.json          # Generation details
│   ├── prompt.txt             # Used prompt
│   ├── raw_response.txt       # Raw AI response
│   ├── content.md             # Markdown format
│   ├── content.html           # HTML format
│   ├── content.json           # JSON format
│   └── content.txt            # Plain text format
└── ...
```

### Session Management Commands
```bash
# List recent sessions
inkforge sessions --list

# Show detailed session information
inkforge sessions --show 20241201_143022

# Clean sessions older than 7 days
inkforge sessions --clean
```

### Customizing Auto-Save
```bash
# Save only specific formats
inkforge generate "Topic" --save-formats "md,txt"

# Disable auto-save completely
inkforge generate "Topic" --no-auto-save

# Default formats (if not specified)
# md,html,json
```
```

## 🏗️ Architecture

InkForge follows a modular architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Interface │────│  Content Generator│────│   AI Service    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────┴────────┐
                       │                 │
                ┌──────▼──────┐   ┌──────▼──────┐
                │   Prompt    │   │ Processors  │
                │  Templates  │   │             │
                └─────────────┘   └─────────────┘
                                         │
                              ┌──────────┼──────────┐
                              │          │          │
                       ┌──────▼──┐ ┌─────▼────┐ ┌──▼────┐
                       │Humanizer│ │Engagement│ │Platform│
                       │         │ │Optimizer │ │Optimizer│
                       └─────────┘ └──────────┘ └───────┘
```

### Core Components

- **CLI Interface**: Interactive command-line interface using Typer
- **Content Generator**: Main orchestrator for content generation
- **AI Service**: Integration with OpenRouter API
- **Prompt Templates**: Dynamic prompt generation based on context
- **Processors**: Content enhancement modules
  - **Humanizer**: Makes AI content feel more natural
  - **Engagement Optimizer**: Adds elements to boost engagement
  - **Platform Optimizer**: Adapts content for specific platforms

## 🌍 Supported Platforms & Countries

### Countries
- 🇺🇸 United States (English)
- 🇨🇳 China (Chinese)
- 🇯🇵 Japan (Japanese)
- 🇫🇷 France (French)
- 🇩🇪 Germany (German)
- 🇬🇧 United Kingdom (English)
- 🇰🇷 South Korea (Korean)
- 🇮🇳 India (English)
- 🇧🇷 Brazil (Portuguese)
- 🇪🇸 Spain (Spanish)

### Platforms
- **Medium**: Long-form articles with subheadings and rich formatting
- **Zhihu**: Q&A format with data support and personal experiences
- **Twitter**: Thread-optimized content with hashtags and emojis
- **Xiaohongshu**: Visual, lifestyle-focused content
- **LinkedIn**: Professional insights with industry statistics
- **Substack**: Newsletter-style content with sections
- **WeChat**: Chinese social media optimization
- **Note**: Japanese blogging platform
- **Generic Blog**: Universal blog format

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/inkforge/inkforge.git
cd inkforge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=inkforge

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests

# Type checking
mypy src
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🌍 Add support for new countries/languages
- 📱 Add new platform optimizations
- 🧪 Write tests
- 🔧 Fix issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenRouter for providing access to various AI models
- The open-source community for inspiration and tools
- All contributors who help make InkForge better

## 📞 Support

- 📖 [Documentation](https://inkforge.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/inkforge/inkforge/issues)
- 💬 [Discussions](https://github.com/inkforge/inkforge/discussions)

---

**Made with ❤️ by the InkForge community**
