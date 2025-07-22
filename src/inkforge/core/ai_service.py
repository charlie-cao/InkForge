"""AI service integration for InkForge."""

import json
import asyncio
from typing import Dict, List, Optional, Any, Union
import httpx
from pydantic import BaseModel

from .config import Config
from ..models.content import GenerationConfig


class AIResponse(BaseModel):
    """AI service response model."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    metadata: Dict[str, Any] = {}


class AIService:
    """AI service client for OpenRouter API."""
    
    def __init__(self, config: Config):
        """Initialize AI service."""
        self.config = config
        self.base_url = config.openrouter_base_url.rstrip('/')
        self.headers = config.get_headers()
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            headers=self.headers,
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def generate_content(
        self,
        prompt: str,
        generation_config: Optional[GenerationConfig] = None
    ) -> AIResponse:
        """Generate content using AI model."""
        if generation_config is None:
            generation_config = GenerationConfig()
        
        # Prepare request payload
        payload = {
            "model": generation_config.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": generation_config.temperature,
            "max_tokens": generation_config.max_tokens,
            "top_p": generation_config.top_p,
            "frequency_penalty": generation_config.frequency_penalty,
            "presence_penalty": generation_config.presence_penalty,
            "stream": False,
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract response data
            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "stop")
            usage = data.get("usage", {})
            
            return AIResponse(
                content=content,
                model=data.get("model", generation_config.model),
                usage=usage,
                finish_reason=finish_reason,
                metadata={
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                }
            )
            
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = error_data.get("error", {}).get("message", str(e))
            except:
                error_detail = str(e)
            
            raise AIServiceError(f"API request failed: {error_detail}") from e
        
        except httpx.RequestError as e:
            raise AIServiceError(f"Network error: {str(e)}") from e
        
        except Exception as e:
            raise AIServiceError(f"Unexpected error: {str(e)}") from e
    
    def generate_content_sync(
        self,
        prompt: str,
        generation_config: Optional[GenerationConfig] = None
    ) -> AIResponse:
        """Synchronous wrapper for content generation."""
        return asyncio.run(self.generate_content(prompt, generation_config))
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()
            
            data = response.json()
            return data.get("data", [])
            
        except Exception as e:
            raise AIServiceError(f"Failed to get models: {str(e)}") from e
    
    def get_available_models_sync(self) -> List[Dict[str, Any]]:
        """Synchronous wrapper for getting available models."""
        return asyncio.run(self.get_available_models())
    
    async def validate_model(self, model_name: str) -> bool:
        """Validate if a model is available."""
        try:
            models = await self.get_available_models()
            available_model_ids = [model.get("id", "") for model in models]
            return model_name in available_model_ids
        except:
            # If we can't get models list, assume the model is valid
            return True
    
    def validate_model_sync(self, model_name: str) -> bool:
        """Synchronous wrapper for model validation."""
        return asyncio.run(self.validate_model(model_name))
    
    async def estimate_cost(
        self,
        prompt: str,
        generation_config: Optional[GenerationConfig] = None
    ) -> Dict[str, Any]:
        """Estimate the cost of generation (if supported by the API)."""
        if generation_config is None:
            generation_config = GenerationConfig()
        
        # Simple token estimation (rough approximation)
        prompt_tokens = len(prompt.split()) * 1.3  # Rough token estimation
        max_completion_tokens = generation_config.max_tokens
        
        return {
            "estimated_prompt_tokens": int(prompt_tokens),
            "max_completion_tokens": max_completion_tokens,
            "total_max_tokens": int(prompt_tokens + max_completion_tokens),
            "model": generation_config.model,
            "note": "This is a rough estimation. Actual costs may vary."
        }
    
    def estimate_cost_sync(
        self,
        prompt: str,
        generation_config: Optional[GenerationConfig] = None
    ) -> Dict[str, Any]:
        """Synchronous wrapper for cost estimation."""
        return asyncio.run(self.estimate_cost(prompt, generation_config))


class AIServiceError(Exception):
    """AI service related errors."""
    pass


class AIServiceManager:
    """Manager for AI service instances."""
    
    def __init__(self, config: Config):
        """Initialize AI service manager."""
        self.config = config
        self._service: Optional[AIService] = None
    
    def get_service(self) -> AIService:
        """Get AI service instance."""
        if self._service is None:
            self._service = AIService(self.config)
        return self._service
    
    async def get_async_service(self) -> AIService:
        """Get async AI service instance."""
        service = AIService(self.config)
        return service
    
    def validate_configuration(self) -> bool:
        """Validate AI service configuration."""
        try:
            # Check if API key is set
            if not self.config.validate_api_key():
                return False

            # For basic validation, just check if we have the API key
            # Model validation can be done later during actual generation
            return True

        except Exception:
            return False
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to AI service."""
        try:
            async with AIService(self.config) as service:
                # Try a simple generation
                test_prompt = "Say 'Hello, InkForge!' in a friendly way."
                config = GenerationConfig(
                    model=self.config.default_model,
                    max_tokens=50,
                    temperature=0.1
                )
                
                response = await service.generate_content(test_prompt, config)
                
                return {
                    "success": True,
                    "model": response.model,
                    "response_time": response.metadata.get("response_time", 0),
                    "usage": response.usage,
                    "test_response": response.content[:100] + "..." if len(response.content) > 100 else response.content
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def test_connection_sync(self) -> Dict[str, Any]:
        """Synchronous wrapper for connection test."""
        return asyncio.run(self.test_connection())
