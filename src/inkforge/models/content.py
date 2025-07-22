"""Content models for InkForge."""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class Country(str, Enum):
    """Supported countries."""
    US = "US"
    CN = "CN"
    JP = "JP"
    FR = "FR"
    DE = "DE"
    UK = "UK"
    KR = "KR"
    IN = "IN"
    BR = "BR"
    ES = "ES"


class Industry(str, Enum):
    """Supported industries."""
    GENERAL = "general"
    FINANCE = "finance"
    HEALTH = "health"
    EDUCATION = "education"
    GAMING = "gaming"
    TECHNOLOGY = "technology"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    TRAVEL = "travel"
    FOOD = "food"


class Platform(str, Enum):
    """Supported platforms."""
    MEDIUM = "medium"
    ZHIHU = "zhihu"
    TWITTER = "twitter"
    XIAOHONGSHU = "xiaohongshu"
    WECHAT = "wechat"
    LINKEDIN = "linkedin"
    SUBSTACK = "substack"
    NOTE = "note"
    BLOG = "blog"


class Tone(str, Enum):
    """Content tone options."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTERTAINING = "entertaining"
    ANALYTICAL = "analytical"
    INSPIRATIONAL = "inspirational"
    NEUTRAL = "neutral"


class Goal(str, Enum):
    """Content goals."""
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    SHARES = "shares"
    COMMENTS = "comments"
    FOLLOWERS = "followers"
    AWARENESS = "awareness"


class OutputFormat(str, Enum):
    """Output format options."""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    PLAIN = "plain"


class ContentRequest(BaseModel):
    """Request model for content generation."""
    
    topic: str = Field(..., description="The main topic or title for the content")
    country: Country = Field(default=Country.US, description="Target country")
    industry: Industry = Field(default=Industry.GENERAL, description="Target industry")
    platform: Platform = Field(default=Platform.MEDIUM, description="Target platform")
    tone: Tone = Field(default=Tone.PROFESSIONAL, description="Content tone")
    goal: Goal = Field(default=Goal.ENGAGEMENT, description="Content goal")
    language: Optional[str] = Field(default=None, description="Target language (auto-detected from country if not specified)")
    keywords: Optional[List[str]] = Field(default=None, description="Keywords to include")
    length: Optional[int] = Field(default=1000, description="Approximate word count", ge=100, le=5000)
    custom_instructions: Optional[str] = Field(default=None, description="Additional custom instructions")
    
    @validator('language', always=True)
    def set_language_from_country(cls, v, values):
        """Set language based on country if not provided."""
        if v is None and 'country' in values:
            country_language_map = {
                Country.US: "en",
                Country.CN: "zh",
                Country.JP: "ja",
                Country.FR: "fr",
                Country.DE: "de",
                Country.UK: "en",
                Country.KR: "ko",
                Country.IN: "en",
                Country.BR: "pt",
                Country.ES: "es",
            }
            return country_language_map.get(values['country'], "en")
        return v


class ContentResponse(BaseModel):
    """Response model for generated content."""
    
    title: str = Field(..., description="Generated title")
    content: str = Field(..., description="Generated content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    engagement_tips: List[str] = Field(default_factory=list, description="Tips for better engagement")
    platform_specific_notes: List[str] = Field(default_factory=list, description="Platform-specific optimization notes")
    word_count: int = Field(..., description="Actual word count")
    estimated_read_time: int = Field(..., description="Estimated reading time in minutes")
    tags: List[str] = Field(default_factory=list, description="Suggested tags")
    
    @validator('estimated_read_time', always=True)
    def calculate_read_time(cls, v, values):
        """Calculate estimated reading time based on word count."""
        if 'word_count' in values:
            # Average reading speed: 200 words per minute
            return max(1, round(values['word_count'] / 200))
        return v or 1


class GenerationConfig(BaseModel):
    """Configuration for content generation."""
    
    model: str = Field(default="mistralai/mistral-small-3.2-24b-instruct:free", description="AI model to use")
    temperature: float = Field(default=0.7, description="Generation temperature", ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, description="Maximum tokens to generate", ge=100, le=8000)
    top_p: float = Field(default=0.9, description="Top-p sampling parameter", ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, description="Frequency penalty", ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, description="Presence penalty", ge=-2.0, le=2.0)
    
    # Processing options
    enable_humanization: bool = Field(default=True, description="Enable humanization processing")
    enable_engagement_optimization: bool = Field(default=True, description="Enable engagement optimization")
    enable_platform_optimization: bool = Field(default=True, description="Enable platform-specific optimization")
    
    # Quality control
    min_quality_score: float = Field(default=0.7, description="Minimum quality score threshold", ge=0.0, le=1.0)
    max_retries: int = Field(default=3, description="Maximum generation retries", ge=1, le=10)
