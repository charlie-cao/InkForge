# Contributing to InkForge

Thank you for your interest in contributing to InkForge! We welcome contributions from everyone, whether you're fixing a bug, adding a feature, improving documentation, or helping with translations.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/inkforge.git
   cd inkforge
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

5. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

6. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run these tools before committing:

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

Or run all checks at once:
```bash
pre-commit run --all-files
```

### Testing

We use pytest for testing. Please ensure all tests pass before submitting a PR:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=inkforge

# Run specific test file
pytest tests/test_models.py
```

### Writing Tests

- Write tests for all new functionality
- Aim for high test coverage
- Use descriptive test names
- Follow the existing test structure

Example test:
```python
def test_content_request_creation():
    """Test creating a content request."""
    request = ContentRequest(
        topic="Test Topic",
        country=Country.US
    )
    assert request.topic == "Test Topic"
    assert request.country == Country.US
```

## 📝 Types of Contributions

### 🐛 Bug Reports

When reporting bugs, please include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, Python version, InkForge version)
- Any relevant error messages or logs

Use our bug report template when creating an issue.

### 💡 Feature Requests

For feature requests, please:

- Use a clear, descriptive title
- Explain the problem you're trying to solve
- Describe your proposed solution
- Consider alternative solutions
- Explain why this feature would be useful to other users

### 🔧 Code Contributions

#### Small Changes
For small changes (bug fixes, documentation improvements):
1. Create a branch
2. Make your changes
3. Add tests if applicable
4. Submit a pull request

#### Large Changes
For significant changes (new features, major refactoring):
1. Open an issue first to discuss the change
2. Wait for maintainer feedback
3. Create a branch and implement the change
4. Submit a pull request

### 🌍 Localization

We welcome contributions for new countries and languages:

1. **Add country/language support**:
   - Update `Country` enum in `models/content.py`
   - Add language mapping in `ContentRequest.set_language_from_country`

2. **Create prompt templates**:
   - Add templates in `templates/prompts/`
   - Update `prompt_manager.py` mappings

3. **Add platform support**:
   - Update `Platform` enum
   - Create platform optimizer in `processors/platform_optimizer.py`

### 📚 Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples
- Improve API documentation
- Translate documentation to other languages

## 🔄 Pull Request Process

1. **Update documentation** if your changes affect the public API
2. **Add tests** for new functionality
3. **Update the changelog** if applicable
4. **Ensure all checks pass** (tests, linting, type checking)
5. **Write a clear PR description** explaining your changes

### PR Title Format
Use conventional commit format:
- `feat: add support for new platform`
- `fix: resolve issue with content generation`
- `docs: update installation instructions`
- `test: add tests for humanizer module`

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for changes
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 🏷️ Issue Labels

We use labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `question`: Further information requested
- `wontfix`: This will not be worked on

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and considerate
- Use inclusive language
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions

## 🎯 Priorities

Current priority areas for contributions:

1. **Platform Support**: Adding new social media platforms
2. **Localization**: Supporting more countries and languages
3. **Content Quality**: Improving humanization and engagement
4. **Performance**: Optimizing generation speed
5. **Documentation**: Improving guides and examples

## 📞 Getting Help

If you need help:

1. Check existing documentation
2. Search existing issues
3. Ask in GitHub Discussions
4. Create a new issue with the `question` label

## 🙏 Recognition

Contributors are recognized in:

- The project README
- Release notes
- GitHub contributors page

Thank you for contributing to InkForge! 🔥
