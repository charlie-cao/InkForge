#!/usr/bin/env python3
"""Test OpenRouter API directly."""

import os
import sys
import asyncio
import httpx
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_api():
    """Test OpenRouter API directly."""
    api_key = os.getenv('OPENROUTER_API_KEY')
    print(f"API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/inkforge/inkforge",
        "X-Title": "InkForge - AI Blog Generator",
    }
    
    payload = {
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": "Say hello in a friendly way."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": False,
    }
    
    print("Testing OpenRouter API...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API call successful!")
                print(f"Model: {data.get('model', 'Unknown')}")
                print(f"Usage: {data.get('usage', {})}")
                if 'choices' in data and data['choices']:
                    content = data['choices'][0]['message']['content']
                    print(f"Response: {content}")
            else:
                print("❌ API call failed!")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
