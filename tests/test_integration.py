"""Integration tests for InkForge."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from inkforge.core.config import Config
from inkforge.core.generator import ContentGenerator
from inkforge.models.content import ContentRequest, Country, Industry, Platform
from inkforge.utils.formatters import format_content, OutputFormat


class TestIntegration:
    """Integration tests for the complete InkForge workflow."""
    
    @pytest.fixture
    def mock_ai_service(self):
        """Mock AI service for integration tests."""
        with patch('inkforge.core.ai_service.AIService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value.__aenter__.return_value = mock_instance
            mock_service.return_value.__aexit__.return_value = None
            
            # Mock AI response
            mock_response = Mock()
            mock_response.content = """# The Future of AI in Healthcare

Artificial Intelligence is transforming healthcare in remarkable ways.

## Key Applications

### Diagnostic Imaging
AI systems can detect diseases with high accuracy.

### Drug Discovery
Machine learning accelerates drug development.

## Conclusion

The future looks promising for AI in healthcare.

Tags: AI, healthcare, technology
Engagement Tips: Ask about reader experiences with AI healthcare tools"""
            
            mock_response.model = "test-model"
            mock_response.usage = {"prompt_tokens": 100, "completion_tokens": 200}
            mock_response.finish_reason = "stop"
            mock_response.metadata = {"response_time": 1.5}
            
            mock_instance.generate_content.return_value = mock_response
            
            yield mock_instance
    
    def test_end_to_end_content_generation(self, mock_ai_service):
        """Test complete content generation workflow."""
        # Setup
        config = Config()
        config.openrouter_api_key = "test-key"
        config.enable_humanization = False  # Disable for simpler testing
        config.enable_engagement_optimization = False
        config.enable_platform_optimization = False
        
        generator = ContentGenerator(config)
        
        request = ContentRequest(
            topic="The Future of AI in Healthcare",
            country=Country.US,
            industry=Industry.HEALTH,
            platform=Platform.MEDIUM,
            keywords=["AI", "healthcare"],
            length=500
        )
        
        # Execute
        response = generator.generate(request)
        
        # Verify
        assert response.title
        assert response.content
        assert response.word_count > 0
        assert response.estimated_read_time > 0
        assert "AI" in response.content or "ai" in response.content.lower()
        assert "healthcare" in response.content.lower()
    
    def test_multiple_format_output(self, mock_ai_service):
        """Test generating content in multiple formats."""
        # Setup
        config = Config()
        config.openrouter_api_key = "test-key"
        generator = ContentGenerator(config)
        
        request = ContentRequest(
            topic="Test Topic",
            country=Country.US
        )
        
        # Generate content
        response = generator.generate(request)
        
        # Test different output formats
        formats_to_test = [
            OutputFormat.MARKDOWN,
            OutputFormat.HTML,
            OutputFormat.JSON,
            OutputFormat.PLAIN
        ]
        
        for format_type in formats_to_test:
            formatted_content = format_content(response, format_type)
            assert formatted_content
            assert len(formatted_content) > 0
            
            if format_type == OutputFormat.JSON:
                import json
                # Should be valid JSON
                json.loads(formatted_content)
            elif format_type == OutputFormat.HTML:
                assert "<html>" in formatted_content or "<h1>" in formatted_content
    
    def test_file_output_workflow(self, mock_ai_service):
        """Test complete workflow with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup
            config = Config()
            config.openrouter_api_key = "test-key"
            generator = ContentGenerator(config)
            
            request = ContentRequest(
                topic="Test File Output",
                country=Country.US
            )
            
            # Generate content
            response = generator.generate(request)
            
            # Save to different formats
            output_dir = Path(temp_dir)
            
            # Markdown
            md_file = output_dir / "test.md"
            format_content(response, OutputFormat.MARKDOWN, md_file)
            assert md_file.exists()
            assert md_file.read_text(encoding='utf-8')
            
            # HTML
            html_file = output_dir / "test.html"
            format_content(response, OutputFormat.HTML, html_file)
            assert html_file.exists()
            assert html_file.read_text(encoding='utf-8')
            
            # JSON
            json_file = output_dir / "test.json"
            format_content(response, OutputFormat.JSON, json_file)
            assert json_file.exists()
            
            # Verify JSON content
            import json
            json_data = json.loads(json_file.read_text(encoding='utf-8'))
            assert json_data["title"] == response.title
    
    def test_different_countries_and_platforms(self, mock_ai_service):
        """Test content generation for different countries and platforms."""
        config = Config()
        config.openrouter_api_key = "test-key"
        generator = ContentGenerator(config)
        
        test_cases = [
            (Country.US, Platform.MEDIUM),
            (Country.CN, Platform.ZHIHU),
            (Country.JP, Platform.NOTE),
        ]
        
        for country, platform in test_cases:
            request = ContentRequest(
                topic="Technology Trends",
                country=country,
                platform=platform,
                length=300
            )
            
            response = generator.generate(request)
            
            # Basic validation
            assert response.title
            assert response.content
            assert response.word_count > 0
            
            # Language should be set correctly
            assert request.language is not None
    
    def test_error_handling(self):
        """Test error handling in integration scenarios."""
        # Test without API key
        config = Config()
        # Don't set API key
        generator = ContentGenerator(config)
        
        request = ContentRequest(topic="Test")
        
        with pytest.raises(ValueError, match="API key"):
            generator.generate(request)
    
    def test_configuration_integration(self):
        """Test configuration integration."""
        # Test with environment variables
        env_vars = {
            'OPENROUTER_API_KEY': 'test-env-key',
            'DEFAULT_MODEL': 'test-env-model',
            'DEFAULT_COUNTRY': 'CN',
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            assert config.openrouter_api_key == 'test-env-key'
            assert config.default_model == 'test-env-model'
            assert config.default_country == 'CN'
            
            # Should be able to create generator
            generator = ContentGenerator(config)
            assert generator.config.openrouter_api_key == 'test-env-key'
    
    def test_prompt_template_integration(self, mock_ai_service):
        """Test prompt template system integration."""
        config = Config()
        config.openrouter_api_key = "test-key"
        generator = ContentGenerator(config)
        
        # Test different combinations that should generate different prompts
        test_cases = [
            ContentRequest(
                topic="Finance Tips",
                country=Country.US,
                industry=Industry.FINANCE,
                platform=Platform.MEDIUM
            ),
            ContentRequest(
                topic="健康生活",
                country=Country.CN,
                industry=Industry.HEALTH,
                platform=Platform.ZHIHU
            ),
        ]
        
        for request in test_cases:
            # This should not raise an error and should generate content
            response = generator.generate(request)
            assert response.title
            assert response.content
    
    @pytest.mark.slow
    def test_performance_benchmark(self, mock_ai_service):
        """Basic performance test."""
        import time
        
        config = Config()
        config.openrouter_api_key = "test-key"
        generator = ContentGenerator(config)
        
        request = ContentRequest(
            topic="Performance Test",
            length=1000
        )
        
        start_time = time.time()
        response = generator.generate(request)
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        # Should complete within reasonable time (mocked, so should be fast)
        assert generation_time < 5.0  # 5 seconds max
        assert response.word_count > 0
    
    def test_quality_control_integration(self, mock_ai_service):
        """Test quality control mechanisms."""
        config = Config()
        config.openrouter_api_key = "test-key"
        config.min_quality_score = 0.5  # Lower threshold for testing
        
        generator = ContentGenerator(config)
        
        request = ContentRequest(
            topic="Quality Test",
            keywords=["test", "quality"],
            length=500
        )
        
        response = generator.generate(request)
        
        # Should have generated content that passes quality checks
        assert response.title
        assert response.content
        assert response.word_count > 0
        
        # Should not have quality warnings in metadata (since we're mocking good content)
        assert "quality_warning" not in response.metadata
