"""Tests for InkForge configuration."""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
import toml

from inkforge.core.config import Config


class TestConfig:
    """Test Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.openrouter_api_key is None
        assert config.openrouter_base_url == "https://openrouter.ai/api/v1"
        assert config.default_model == "mistralai/mistral-small-3.2-24b-instruct:free"
        assert config.default_country == "US"
        assert config.default_industry == "general"
        assert config.default_platform == "medium"
        assert config.default_tone == "professional"
        assert config.default_goal == "engagement"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.enable_humanization is True
        assert config.debug is False
    
    def test_env_var_loading(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            'OPENROUTER_API_KEY': 'test-api-key',
            'DEFAULT_MODEL': 'test-model',
            'DEFAULT_COUNTRY': 'CN',
            'DEFAULT_INDUSTRY': 'finance',
            'MAX_CONTENT_LENGTH': '3000',
            'DEBUG': 'true',
            'TEMPERATURE': '0.8',
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            assert config.openrouter_api_key == 'test-api-key'
            assert config.default_model == 'test-model'
            assert config.default_country == 'CN'
            assert config.default_industry == 'finance'
            assert config.max_content_length == 3000
            assert config.debug is True
            assert config.temperature == 0.8
    
    def test_json_config_loading(self):
        """Test loading configuration from JSON file."""
        config_data = {
            'openrouter_api_key': 'json-api-key',
            'default_model': 'json-model',
            'default_country': 'JP',
            'temperature': 0.9,
            'debug': True,
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            config = Config(config_file=config_file)
            
            assert config.openrouter_api_key == 'json-api-key'
            assert config.default_model == 'json-model'
            assert config.default_country == 'JP'
            assert config.temperature == 0.9
            assert config.debug is True
        finally:
            config_file.unlink()
    
    def test_toml_config_loading(self):
        """Test loading configuration from TOML file."""
        config_data = {
            'openrouter_api_key': 'toml-api-key',
            'default_model': 'toml-model',
            'default_country': 'FR',
            'temperature': 0.6,
            'enable_humanization': False,
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            toml.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            config = Config(config_file=config_file)
            
            assert config.openrouter_api_key == 'toml-api-key'
            assert config.default_model == 'toml-model'
            assert config.default_country == 'FR'
            assert config.temperature == 0.6
            assert config.enable_humanization is False
        finally:
            config_file.unlink()
    
    def test_config_precedence(self):
        """Test configuration precedence (file overrides env, explicit overrides both)."""
        # Set environment variable
        env_vars = {
            'OPENROUTER_API_KEY': 'env-key',
            'DEFAULT_MODEL': 'env-model',
        }
        
        # Create config file
        config_data = {
            'openrouter_api_key': 'file-key',
            'default_country': 'DE',
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            with patch.dict(os.environ, env_vars):
                config = Config(config_file=config_file)
                
                # File should override env
                assert config.openrouter_api_key == 'file-key'
                # Env should be used if not in file
                assert config.default_model == 'env-model'
                # File-only setting
                assert config.default_country == 'DE'
        finally:
            config_file.unlink()
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        
        # Test country validation
        config.default_country = 'invalid'
        assert config.default_country == 'US'  # Should fallback to default
        
        config.default_country = 'cn'
        assert config.default_country == 'CN'  # Should be uppercase
        
        # Test industry validation
        config.default_industry = 'invalid'
        assert config.default_industry == 'general'  # Should fallback to default
        
        config.default_industry = 'FINANCE'
        assert config.default_industry == 'finance'  # Should be lowercase
    
    def test_api_key_validation(self):
        """Test API key validation."""
        config = Config()
        
        # No API key
        assert not config.validate_api_key()
        
        # Empty API key
        config.openrouter_api_key = ""
        assert not config.validate_api_key()
        
        # Whitespace only
        config.openrouter_api_key = "   "
        assert not config.validate_api_key()
        
        # Valid API key
        config.openrouter_api_key = "sk-test-key"
        assert config.validate_api_key()
    
    def test_get_headers(self):
        """Test HTTP headers generation."""
        config = Config()
        config.openrouter_api_key = "test-key"
        
        headers = config.get_headers()
        
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["Content-Type"] == "application/json"
        assert "HTTP-Referer" in headers
        assert "X-Title" in headers
    
    def test_get_headers_no_key(self):
        """Test headers generation without API key."""
        config = Config()
        
        with pytest.raises(ValueError, match="OpenRouter API key not configured"):
            config.get_headers()
    
    def test_config_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.toml"
            
            # Create and save config
            config1 = Config()
            config1.openrouter_api_key = "test-save-key"
            config1.default_model = "test-save-model"
            config1.temperature = 0.5
            config1.save(config_file)
            
            # Load config
            config2 = Config(config_file=config_file)
            
            assert config2.openrouter_api_key == "test-save-key"
            assert config2.default_model == "test-save-model"
            assert config2.temperature == 0.5
    
    def test_config_set_and_get(self):
        """Test setting and getting configuration values."""
        config = Config()
        
        # Test set
        config.set('default_model', 'new-model')
        assert config.default_model == 'new-model'
        
        # Test get
        assert config.get('default_model') == 'new-model'
        assert config.get('nonexistent_key', 'default') == 'default'
        
        # Test invalid key
        with pytest.raises(ValueError, match="Unknown configuration key"):
            config.set('invalid_key', 'value')
    
    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        config = Config()
        
        # Modify some values
        config.openrouter_api_key = "test-key"
        config.default_model = "custom-model"
        config.temperature = 0.9
        
        # Reset to defaults
        config.reset_to_defaults()
        
        assert config.openrouter_api_key is None
        assert config.default_model == "mistralai/mistral-small-3.2-24b-instruct:free"
        assert config.temperature == 0.7
    
    def test_debug_mode(self):
        """Test debug mode initialization."""
        # Debug from parameter
        config = Config(debug=True)
        assert config.debug is True
        
        # Debug from environment
        with patch.dict(os.environ, {'DEBUG': 'true'}):
            config = Config()
            assert config.debug is True
        
        # Debug false
        with patch.dict(os.environ, {'DEBUG': 'false'}):
            config = Config()
            assert config.debug is False
