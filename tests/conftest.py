"""Pytest configuration and fixtures for InkForge tests."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from inkforge.core.config import Config
from inkforge.models.content import ContentRequest, ContentResponse, Country, Industry, Platform


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Config()
    config.openrouter_api_key = "test-api-key"
    config.default_model = "test-model"
    config.debug = True
    return config


@pytest.fixture
def sample_content_request():
    """Create a sample ContentRequest for testing."""
    return ContentRequest(
        topic="The Future of AI in Healthcare",
        country=Country.US,
        industry=Industry.HEALTH,
        platform=Platform.MEDIUM,
        keywords=["AI", "healthcare", "technology", "future"],
        length=1000,
        custom_instructions="Focus on practical applications"
    )


@pytest.fixture
def sample_content_response():
    """Create a sample ContentResponse for testing."""
    return ContentResponse(
        title="The Future of AI in Healthcare: Transforming Patient Care",
        content="""# Introduction

Artificial Intelligence is revolutionizing healthcare in unprecedented ways. From diagnostic imaging to personalized treatment plans, AI technologies are transforming how we approach patient care.

## Key Applications

### Diagnostic Imaging
AI-powered systems can now detect diseases in medical images with accuracy that often surpasses human specialists.

### Drug Discovery
Machine learning algorithms are accelerating the drug discovery process, potentially reducing development time from decades to years.

### Personalized Medicine
AI enables the creation of treatment plans tailored to individual patients based on their genetic makeup and medical history.

## Challenges and Considerations

While the potential is enormous, we must address concerns about data privacy, algorithmic bias, and the need for regulatory frameworks.

## Conclusion

The future of AI in healthcare is bright, but it requires careful implementation and ongoing collaboration between technologists and healthcare professionals.""",
        word_count=150,
        estimated_read_time=1,
        tags=["AI", "healthcare", "technology", "medicine"],
        engagement_tips=[
            "Ask readers about their experiences with AI in healthcare",
            "Share specific examples of AI applications they might have encountered"
        ],
        platform_specific_notes=[
            "Use subheadings for better Medium readability",
            "Include relevant statistics to support claims"
        ],
        metadata={
            "generation_model": "test-model",
            "generation_time": "2024-01-01T12:00:00Z",
            "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
        }
    )


@pytest.fixture
def mock_ai_response():
    """Create a mock AI response for testing."""
    mock_response = Mock()
    mock_response.content = """# The Future of AI in Healthcare

This is a test blog post about AI in healthcare.

## Key Benefits

- Improved diagnostics
- Faster drug discovery
- Personalized treatment

Tags: AI, healthcare, technology
Engagement Tips: Ask questions about reader experiences"""
    mock_response.model = "test-model"
    mock_response.usage = {"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150}
    mock_response.finish_reason = "stop"
    mock_response.metadata = {"response_time": 2.5, "status_code": 200}
    return mock_response


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'OPENROUTER_API_KEY': 'test-env-api-key',
        'DEFAULT_MODEL': 'test-env-model',
        'DEFAULT_COUNTRY': 'US',
        'DEBUG': 'true'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before each test."""
    # Store original values
    original_env = {}
    inkforge_env_vars = [
        'OPENROUTER_API_KEY',
        'OPENROUTER_BASE_URL',
        'DEFAULT_MODEL',
        'DEFAULT_COUNTRY',
        'DEFAULT_INDUSTRY',
        'DEFAULT_PLATFORM',
        'DEBUG'
    ]
    
    for var in inkforge_env_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original_env.items():
        os.environ[var] = value


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for API testing."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = Mock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        mock_client.return_value.__aexit__.return_value = None
        yield mock_instance
