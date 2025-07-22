#!/usr/bin/env python3
"""Test CLI environment variable loading."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables early (same as CLI)
from dotenv import load_dotenv
load_dotenv()

print("Environment variables after load_dotenv():")
print(f"OPENROUTER_API_KEY: {os.getenv('OPENROUTER_API_KEY')}")

# Test config creation (same as CLI)
from inkforge.core.config import Config

config = Config()
print(f"\nConfig after creation:")
print(f"API key: {config.openrouter_api_key}")
print(f"Validation: {config.validate_api_key()}")

if config.validate_api_key():
    print("✅ Configuration is valid")
    try:
        headers = config.get_headers()
        print(f"Headers created successfully: {list(headers.keys())}")
    except Exception as e:
        print(f"❌ Failed to create headers: {e}")
else:
    print("❌ Configuration is invalid")
