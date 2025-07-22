#!/usr/bin/env python3
"""Test AI service configuration."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables early (same as CLI)
from dotenv import load_dotenv
load_dotenv()

print("Testing AI Service configuration...")

from inkforge.core.config import Config
from inkforge.core.ai_service import AIService

# Create config
config = Config()
print(f"Config API key: {config.openrouter_api_key}")
print(f"Config validation: {config.validate_api_key()}")

# Test headers
try:
    headers = config.get_headers()
    print(f"Headers: {headers}")
except Exception as e:
    print(f"Failed to get headers: {e}")

# Test AI service creation
try:
    ai_service = AIService(config)
    print(f"AI service created successfully")
    print(f"AI service headers: {ai_service.headers}")
except Exception as e:
    print(f"Failed to create AI service: {e}")
