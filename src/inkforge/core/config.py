"""Configuration management for InkForge."""

import os
import json
import toml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator

from ..models.content import Country, Industry, Platform, Tone, Goal, OutputFormat


class Config(BaseModel):
    """InkForge configuration management."""
    
    # API Configuration
    openrouter_api_key: Optional[str] = Field(default=None, description="OpenRouter API key")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter base URL")
    
    # Default AI Model
    default_model: str = Field(default="mistralai/mistral-small-3.2-24b-instruct:free", description="Default AI model")
    
    # Default Generation Settings
    default_country: str = Field(default="US", description="Default target country")
    default_industry: str = Field(default="general", description="Default industry")
    default_platform: str = Field(default="medium", description="Default platform")
    default_tone: str = Field(default="professional", description="Default tone")
    default_goal: str = Field(default="engagement", description="Default goal")
    default_output_format: str = Field(default="markdown", description="Default output format")
    default_output_dir: str = Field(default="./output", description="Default output directory")
    
    # Content Settings
    max_content_length: int = Field(default=2000, description="Maximum content length")
    min_content_length: int = Field(default=500, description="Minimum content length")
    
    # Generation Parameters
    temperature: float = Field(default=0.7, description="Generation temperature", ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, description="Maximum tokens", ge=100, le=8000)
    top_p: float = Field(default=0.9, description="Top-p sampling", ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, description="Frequency penalty", ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, description="Presence penalty", ge=-2.0, le=2.0)
    
    # Processing Options
    enable_humanization: bool = Field(default=True, description="Enable humanization processing")
    enable_engagement_optimization: bool = Field(default=True, description="Enable engagement optimization")
    enable_platform_optimization: bool = Field(default=True, description="Enable platform-specific optimization")
    
    # Quality Control
    min_quality_score: float = Field(default=0.7, description="Minimum quality score", ge=0.0, le=1.0)
    max_retries: int = Field(default=3, description="Maximum generation retries", ge=1, le=10)
    
    # Debug Settings
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Internal
    _config_file: Optional[Path] = None
    _config_dir: Optional[Path] = None
    
    class Config:
        """Pydantic config."""
        extra = "allow"
        validate_assignment = True
    
    def __init__(self, config_file: Optional[Path] = None, debug: bool = False, **kwargs):
        """Initialize configuration."""
        # Load .env file if it exists
        from dotenv import load_dotenv
        load_dotenv()

        # Set debug mode first
        if debug:
            kwargs['debug'] = debug

        # Load from environment variables
        env_config = self._load_from_env()
        kwargs.update(env_config)
        
        # Load from config file
        if config_file:
            file_config = self._load_from_file(config_file)
            kwargs.update(file_config)
            self._config_file = config_file
        else:
            # Try to find default config file
            default_config = self._find_default_config()
            if default_config:
                file_config = self._load_from_file(default_config)
                kwargs.update(file_config)
                self._config_file = default_config
        
        super().__init__(**kwargs)
        
        # Set config directory
        if self._config_file:
            self._config_dir = self._config_file.parent
        else:
            self._config_dir = self._get_default_config_dir()
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_mapping = {
            'OPENROUTER_API_KEY': 'openrouter_api_key',
            'OPENROUTER_BASE_URL': 'openrouter_base_url',
            'DEFAULT_MODEL': 'default_model',
            'DEFAULT_COUNTRY': 'default_country',
            'DEFAULT_INDUSTRY': 'default_industry',
            'DEFAULT_PLATFORM': 'default_platform',
            'DEFAULT_TONE': 'default_tone',
            'DEFAULT_GOAL': 'default_goal',
            'DEFAULT_OUTPUT_FORMAT': 'default_output_format',
            'DEFAULT_OUTPUT_DIR': 'default_output_dir',
            'MAX_CONTENT_LENGTH': 'max_content_length',
            'MIN_CONTENT_LENGTH': 'min_content_length',
            'DEBUG': 'debug',
            'LOG_LEVEL': 'log_level',
        }
        
        config = {}
        for env_key, config_key in env_mapping.items():
            value = os.getenv(env_key)
            if value is not None:
                # Convert string values to appropriate types
                if config_key in ['max_content_length', 'min_content_length']:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif config_key == 'debug':
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif config_key in ['temperature', 'top_p', 'frequency_penalty', 'presence_penalty', 'min_quality_score']:
                    try:
                        value = float(value)
                    except ValueError:
                        continue
                elif config_key == 'max_tokens':
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                
                config[config_key] = value
        
        return config
    
    def _load_from_file(self, config_file: Path) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_file.exists():
            return {}
        
        try:
            if config_file.suffix.lower() == '.json':
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif config_file.suffix.lower() in ['.toml', '.tml']:
                return toml.load(config_file)
            else:
                # Try to parse as TOML first, then JSON
                try:
                    return toml.load(config_file)
                except:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
        except Exception as e:
            if self.debug:
                print(f"Warning: Could not load config file {config_file}: {e}")
            return {}
    
    def _find_default_config(self) -> Optional[Path]:
        """Find default configuration file."""
        possible_locations = [
            Path.cwd() / "inkforge.toml",
            Path.cwd() / "inkforge.json",
            Path.cwd() / ".inkforge.toml",
            Path.cwd() / ".inkforge.json",
            Path.home() / ".inkforge" / "config.toml",
            Path.home() / ".inkforge" / "config.json",
        ]
        
        for location in possible_locations:
            if location.exists():
                return location
        
        return None
    
    def _get_default_config_dir(self) -> Path:
        """Get default configuration directory."""
        config_dir = Path.home() / ".inkforge"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    def save(self, config_file: Optional[Path] = None) -> None:
        """Save configuration to file."""
        if config_file is None:
            if self._config_file:
                config_file = self._config_file
            else:
                config_file = self._get_default_config_dir() / "config.toml"
        
        # Ensure directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare config data (exclude private fields)
        config_data = self.dict(exclude={'_config_file', '_config_dir'})
        
        # Save based on file extension
        if config_file.suffix.lower() == '.json':
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        else:
            with open(config_file, 'w', encoding='utf-8') as f:
                toml.dump(config_data, f)
        
        self._config_file = config_file
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        if hasattr(self, key):
            setattr(self, key, value)
            # Auto-save if we have a config file
            if self._config_file:
                self.save()
        else:
            raise ValueError(f"Unknown configuration key: {key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(self, key, default)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        # Create a new instance with defaults
        defaults = Config()
        
        # Copy default values
        for field_name, field in self.__fields__.items():
            if not field_name.startswith('_'):
                setattr(self, field_name, getattr(defaults, field_name))
        
        # Save if we have a config file
        if self._config_file:
            self.save()
    
    def validate_api_key(self) -> bool:
        """Validate that API key is set."""
        return bool(self.openrouter_api_key and self.openrouter_api_key.strip())
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        if not self.validate_api_key():
            raise ValueError("OpenRouter API key not configured. Please set OPENROUTER_API_KEY environment variable or use 'inkforge config --set openrouter_api_key --value YOUR_KEY'")
        
        return {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/inkforge/inkforge",
            "X-Title": "InkForge - AI Blog Generator",
        }
    
    @validator('default_country')
    def validate_country(cls, v):
        """Validate country code."""
        try:
            Country(v.upper())
            return v.upper()
        except ValueError:
            return "US"
    
    @validator('default_industry')
    def validate_industry(cls, v):
        """Validate industry."""
        try:
            Industry(v.lower())
            return v.lower()
        except ValueError:
            return "general"
    
    @validator('default_platform')
    def validate_platform(cls, v):
        """Validate platform."""
        try:
            Platform(v.lower())
            return v.lower()
        except ValueError:
            return "medium"
