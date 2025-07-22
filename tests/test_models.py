"""Tests for InkForge models."""

import pytest
from pydantic import ValidationError

from inkforge.models.content import (
    Country, Industry, Platform, Tone, Goal, OutputFormat,
    ContentRequest, ContentResponse, GenerationConfig
)


class TestContentRequest:
    """Test ContentRequest model."""
    
    def test_content_request_creation(self):
        """Test creating a content request."""
        request = ContentRequest(
            topic="Test Topic",
            country=Country.US,
            industry=Industry.TECHNOLOGY,
            platform=Platform.MEDIUM,
            tone=Tone.PROFESSIONAL,
            goal=Goal.ENGAGEMENT
        )
        
        assert request.topic == "Test Topic"
        assert request.country == Country.US
        assert request.industry == Industry.TECHNOLOGY
        assert request.platform == Platform.MEDIUM
        assert request.tone == Tone.PROFESSIONAL
        assert request.goal == Goal.ENGAGEMENT
        assert request.language == "en"  # Auto-detected from country
    
    def test_content_request_defaults(self):
        """Test default values."""
        request = ContentRequest(topic="Test")
        
        assert request.country == Country.US
        assert request.industry == Industry.GENERAL
        assert request.platform == Platform.MEDIUM
        assert request.tone == Tone.PROFESSIONAL
        assert request.goal == Goal.ENGAGEMENT
        assert request.length == 1000
        assert request.language == "en"
    
    def test_language_auto_detection(self):
        """Test automatic language detection from country."""
        # Chinese
        request = ContentRequest(topic="Test", country=Country.CN)
        assert request.language == "zh"
        
        # Japanese
        request = ContentRequest(topic="Test", country=Country.JP)
        assert request.language == "ja"
        
        # French
        request = ContentRequest(topic="Test", country=Country.FR)
        assert request.language == "fr"
    
    def test_custom_language_override(self):
        """Test custom language override."""
        request = ContentRequest(
            topic="Test",
            country=Country.CN,
            language="en"  # Override auto-detection
        )
        assert request.language == "en"
    
    def test_length_validation(self):
        """Test length validation."""
        # Valid length
        request = ContentRequest(topic="Test", length=500)
        assert request.length == 500
        
        # Invalid length (too small)
        with pytest.raises(ValidationError):
            ContentRequest(topic="Test", length=50)
        
        # Invalid length (too large)
        with pytest.raises(ValidationError):
            ContentRequest(topic="Test", length=10000)
    
    def test_keywords_handling(self):
        """Test keywords handling."""
        request = ContentRequest(
            topic="Test",
            keywords=["ai", "technology", "future"]
        )
        assert request.keywords == ["ai", "technology", "future"]
        
        # None keywords
        request = ContentRequest(topic="Test", keywords=None)
        assert request.keywords is None


class TestContentResponse:
    """Test ContentResponse model."""
    
    def test_content_response_creation(self):
        """Test creating a content response."""
        response = ContentResponse(
            title="Test Title",
            content="This is test content with multiple words to test word count.",
            word_count=12,
            tags=["test", "content"],
            engagement_tips=["Tip 1", "Tip 2"]
        )
        
        assert response.title == "Test Title"
        assert response.word_count == 12
        assert response.estimated_read_time == 1  # Minimum 1 minute
        assert response.tags == ["test", "content"]
        assert response.engagement_tips == ["Tip 1", "Tip 2"]
    
    def test_read_time_calculation(self):
        """Test reading time calculation."""
        # Short content (< 200 words)
        response = ContentResponse(
            title="Test",
            content="Short content.",
            word_count=50
        )
        assert response.estimated_read_time == 1  # Minimum 1 minute
        
        # Medium content (~400 words)
        response = ContentResponse(
            title="Test",
            content="Medium content.",
            word_count=400
        )
        assert response.estimated_read_time == 2  # 400/200 = 2 minutes
        
        # Long content (~1000 words)
        response = ContentResponse(
            title="Test",
            content="Long content.",
            word_count=1000
        )
        assert response.estimated_read_time == 5  # 1000/200 = 5 minutes
    
    def test_default_values(self):
        """Test default values."""
        response = ContentResponse(
            title="Test",
            content="Test content",
            word_count=10
        )
        
        assert response.metadata == {}
        assert response.engagement_tips == []
        assert response.platform_specific_notes == []
        assert response.tags == []


class TestGenerationConfig:
    """Test GenerationConfig model."""
    
    def test_generation_config_defaults(self):
        """Test default configuration values."""
        config = GenerationConfig()
        
        assert config.model == "mistralai/mistral-small-3.2-24b-instruct:free"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.top_p == 0.9
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0
        assert config.enable_humanization is True
        assert config.enable_engagement_optimization is True
        assert config.enable_platform_optimization is True
        assert config.min_quality_score == 0.7
        assert config.max_retries == 3
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        # Valid parameters
        config = GenerationConfig(
            temperature=0.5,
            max_tokens=1500,
            top_p=0.8,
            frequency_penalty=0.1,
            presence_penalty=-0.1,
            min_quality_score=0.8,
            max_retries=5
        )
        
        assert config.temperature == 0.5
        assert config.max_tokens == 1500
        assert config.top_p == 0.8
        assert config.frequency_penalty == 0.1
        assert config.presence_penalty == -0.1
        assert config.min_quality_score == 0.8
        assert config.max_retries == 5
    
    def test_invalid_parameters(self):
        """Test invalid parameter validation."""
        # Invalid temperature
        with pytest.raises(ValidationError):
            GenerationConfig(temperature=3.0)  # > 2.0
        
        with pytest.raises(ValidationError):
            GenerationConfig(temperature=-0.1)  # < 0.0
        
        # Invalid max_tokens
        with pytest.raises(ValidationError):
            GenerationConfig(max_tokens=50)  # < 100
        
        with pytest.raises(ValidationError):
            GenerationConfig(max_tokens=10000)  # > 8000
        
        # Invalid top_p
        with pytest.raises(ValidationError):
            GenerationConfig(top_p=1.5)  # > 1.0
        
        # Invalid penalties
        with pytest.raises(ValidationError):
            GenerationConfig(frequency_penalty=3.0)  # > 2.0
        
        with pytest.raises(ValidationError):
            GenerationConfig(presence_penalty=-3.0)  # < -2.0
        
        # Invalid quality score
        with pytest.raises(ValidationError):
            GenerationConfig(min_quality_score=1.5)  # > 1.0
        
        # Invalid retries
        with pytest.raises(ValidationError):
            GenerationConfig(max_retries=0)  # < 1


class TestEnums:
    """Test enum values."""
    
    def test_country_enum(self):
        """Test Country enum."""
        assert Country.US == "US"
        assert Country.CN == "CN"
        assert Country.JP == "JP"
        assert len(Country) == 10  # Check we have all expected countries
    
    def test_industry_enum(self):
        """Test Industry enum."""
        assert Industry.GENERAL == "general"
        assert Industry.FINANCE == "finance"
        assert Industry.TECHNOLOGY == "technology"
        assert len(Industry) == 10  # Check we have all expected industries
    
    def test_platform_enum(self):
        """Test Platform enum."""
        assert Platform.MEDIUM == "medium"
        assert Platform.ZHIHU == "zhihu"
        assert Platform.TWITTER == "twitter"
        assert len(Platform) == 9  # Check we have all expected platforms
    
    def test_tone_enum(self):
        """Test Tone enum."""
        assert Tone.PROFESSIONAL == "professional"
        assert Tone.CASUAL == "casual"
        assert Tone.ENTERTAINING == "entertaining"
        assert len(Tone) == 6  # Check we have all expected tones
    
    def test_goal_enum(self):
        """Test Goal enum."""
        assert Goal.ENGAGEMENT == "engagement"
        assert Goal.CONVERSION == "conversion"
        assert Goal.SHARES == "shares"
        assert len(Goal) == 6  # Check we have all expected goals
    
    def test_output_format_enum(self):
        """Test OutputFormat enum."""
        assert OutputFormat.MARKDOWN == "markdown"
        assert OutputFormat.HTML == "html"
        assert OutputFormat.JSON == "json"
        assert OutputFormat.PLAIN == "plain"
        assert len(OutputFormat) == 4  # Check we have all expected formats
