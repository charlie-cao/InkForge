#!/usr/bin/env python3
"""Test environment variable loading."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from inkforge.core.config import Config

print("Testing environment variable loading...")

# Load .env file
load_dotenv()

print(f"OPENROUTER_API_KEY from os.getenv: {os.getenv('OPENROUTER_API_KEY')}")

# Test config
config = Config()
print(f"Config API key: {config.openrouter_api_key}")
print(f"Config validation: {config.validate_api_key()}")

if config.validate_api_key():
    print("✅ API key is valid")
else:
    print("❌ API key is invalid or missing")
