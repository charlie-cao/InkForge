#!/usr/bin/env python3
"""
Basic test script to verify InkForge functionality.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from inkforge import __version__
        print(f"✅ InkForge version: {__version__}")
    except ImportError as e:
        print(f"❌ Failed to import inkforge: {e}")
        return False
    
    try:
        from inkforge.models.content import ContentRequest, ContentResponse
        print("✅ Models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import models: {e}")
        return False
    
    try:
        from inkforge.core.config import Config
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from inkforge.core.generator import ContentGenerator
        print("✅ Generator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import generator: {e}")
        return False
    
    try:
        from inkforge.utils.formatters import format_content
        print("✅ Formatters imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import formatters: {e}")
        return False
    
    return True

def test_config():
    """Test configuration functionality."""
    print("\nTesting configuration...")
    
    try:
        from inkforge.core.config import Config
        
        config = Config()
        print(f"✅ Config created with default model: {config.default_model}")
        print(f"✅ Default country: {config.default_country}")
        print(f"✅ Default platform: {config.default_platform}")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_models():
    """Test model creation."""
    print("\nTesting models...")
    
    try:
        from inkforge.models.content import ContentRequest, Country, Industry, Platform
        
        request = ContentRequest(
            topic="Test Topic",
            country=Country.US,
            industry=Industry.TECHNOLOGY,
            platform=Platform.MEDIUM
        )
        
        print(f"✅ ContentRequest created: {request.topic}")
        print(f"✅ Language auto-detected: {request.language}")
        
        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False

def test_prompt_manager():
    """Test prompt manager."""
    print("\nTesting prompt manager...")
    
    try:
        from inkforge.templates.prompt_manager import PromptManager
        from inkforge.models.content import ContentRequest, Country, Platform
        
        pm = PromptManager()
        
        request = ContentRequest(
            topic="Test AI Article",
            country=Country.US,
            platform=Platform.MEDIUM
        )
        
        prompt = pm.generate_prompt(request)
        print(f"✅ Prompt generated ({len(prompt)} characters)")
        print(f"✅ Contains topic: {'Test AI Article' in prompt}")
        
        return True
    except Exception as e:
        print(f"❌ Prompt manager test failed: {e}")
        return False

def test_formatters():
    """Test output formatters."""
    print("\nTesting formatters...")
    
    try:
        from inkforge.models.content import ContentResponse, OutputFormat
        from inkforge.utils.formatters import format_content
        
        response = ContentResponse(
            title="Test Title",
            content="This is test content.",
            word_count=4,
            estimated_read_time=1,
            tags=["test"]
        )
        
        # Test Markdown format
        md_output = format_content(response, OutputFormat.MARKDOWN)
        print(f"✅ Markdown format generated ({len(md_output)} characters)")
        
        # Test JSON format
        json_output = format_content(response, OutputFormat.JSON)
        print(f"✅ JSON format generated ({len(json_output)} characters)")
        
        return True
    except Exception as e:
        print(f"❌ Formatters test failed: {e}")
        return False

def test_cli_import():
    """Test CLI import."""
    print("\nTesting CLI import...")
    
    try:
        from inkforge.cli import app
        print("✅ CLI app imported successfully")
        return True
    except Exception as e:
        print(f"❌ CLI import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔥 InkForge Basic Functionality Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_models,
        test_prompt_manager,
        test_formatters,
        test_cli_import,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! InkForge is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
