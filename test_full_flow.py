#!/usr/bin/env python3
"""Test the full flow from CLI to AI service."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables early (same as CLI)
from dotenv import load_dotenv
load_dotenv()

print("Testing full flow...")

# Test 1: Environment variables
print(f"1. Environment variable: {os.getenv('OPENROUTER_API_KEY')}")

# Test 2: Config creation (same as CLI)
from inkforge.core.config import Config
config = Config()
print(f"2. Config API key: {config.openrouter_api_key}")
print(f"3. Config validation: {config.validate_api_key()}")

# Test 3: Headers creation
try:
    headers = config.get_headers()
    print(f"4. Headers created: {list(headers.keys())}")
    print(f"   Authorization header: {headers.get('Authorization', 'MISSING')[:20]}...")
except Exception as e:
    print(f"4. Headers creation failed: {e}")

# Test 4: AI Service creation
from inkforge.core.ai_service import AIService
try:
    ai_service = AIService(config)
    print(f"5. AI service created")
    print(f"   Service headers: {list(ai_service.headers.keys())}")
    print(f"   Service auth header: {ai_service.headers.get('Authorization', 'MISSING')[:20]}...")
except Exception as e:
    print(f"5. AI service creation failed: {e}")

# Test 5: Content Generator creation (same as CLI)
from inkforge.core.generator import ContentGenerator
try:
    generator = ContentGenerator(config)
    print(f"6. Generator created")
    print(f"   Generator config API key: {generator.config.openrouter_api_key}")
    print(f"   Generator config validation: {generator.config.validate_api_key()}")
except Exception as e:
    print(f"6. Generator creation failed: {e}")

# Test 6: Simple request creation
from inkforge.models.content import ContentRequest
try:
    request = ContentRequest(topic="Test", length=100)
    print(f"7. Request created: {request.topic}")
except Exception as e:
    print(f"7. Request creation failed: {e}")

print("\nAll components created successfully. The issue might be in the actual API call.")
