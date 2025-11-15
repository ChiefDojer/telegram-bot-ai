"""
AI Services - Unified interface for multiple AI providers
Supports: ChatGPT, Google Gemini, Claude, Grok, Custom LLM
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import httpx

logger = logging.getLogger(__name__)


class AIService(ABC):
    """Base class for AI service providers"""
    
    def __init__(self, api_key: Optional[str] = None, user_id: Optional[int] = None):
        self.api_key = api_key
        self.user_id = user_id
    
    @abstractmethod
    async def generate_response(self, prompt: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """Generate AI response for given prompt"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the service is properly configured"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the AI service"""
        pass
    
    def get_effective_key(self, user_token: Optional[str] = None) -> Optional[str]:
        """Get the effective API key: user token > instance key"""
        return user_token or self.api_key


class ChatGPTService(AIService):
    """OpenAI ChatGPT service"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", user_id: Optional[int] = None):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"), user_id)
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def is_available(self, user_token: Optional[str] = None) -> bool:
        return bool(self.get_effective_key(user_token))
    
    @property
    def name(self) -> str:
        return f"ChatGPT ({self.model})"
    
    async def generate_response(self, prompt: str, conversation_history: Optional[List[Dict]] = None, user_token: Optional[str] = None) -> str:
        effective_key = self.get_effective_key(user_token)
        if not effective_key:
            return "❌ ChatGPT is not configured. Please set your API key with /settoken."
        
        try:
            messages = conversation_history or []
            messages.append({"role": "user", "content": prompt})
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {effective_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 2000,
                        "temperature": 0.7
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        
        except httpx.HTTPStatusError as e:
            logger.error(f"ChatGPT API error: {e}")
            if e.response.status_code == 401:
                return "❌ Invalid API key. Please update your token with /settoken."
            return f"❌ ChatGPT API error: {e.response.status_code}"
        except Exception as e:
            logger.error(f"ChatGPT error: {e}")
            return f"❌ Error: {str(e)}"


class GeminiService(AIService):
    """Google Gemini service"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash", user_id: Optional[int] = None):
        super().__init__(api_key or os.getenv("GEMINI_API_KEY"), user_id)
        self.model = model
    
    def is_available(self, user_token: Optional[str] = None) -> bool:
        return bool(self.get_effective_key(user_token))
    
    @property
    def name(self) -> str:
        return f"Google Gemini ({self.model})"
    
    async def generate_response(self, prompt: str, conversation_history: Optional[List[Dict]] = None, user_token: Optional[str] = None) -> str:
        effective_key = self.get_effective_key(user_token)
        if not effective_key:
            return "❌ Gemini is not configured. Please set your API key with /settoken."
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=effective_key)
            model = genai.GenerativeModel(self.model)
            
            # Build conversation context if history exists
            full_prompt = prompt
            if conversation_history:
                context = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in conversation_history[-5:]  # Last 5 messages
                ])
                full_prompt = f"Context:\n{context}\n\nUser: {prompt}"
            
            response = await model.generate_content_async(full_prompt)
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            if "API_KEY_INVALID" in str(e) or "401" in str(e):
                return "❌ Invalid API key. Please update your token with /settoken."
            return f"❌ Gemini error: {str(e)}"


class ClaudeService(AIService):
    """Anthropic Claude service"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022", user_id: Optional[int] = None):
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY"), user_id)
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    def is_available(self, user_token: Optional[str] = None) -> bool:
        return bool(self.get_effective_key(user_token))
    
    @property
    def name(self) -> str:
        return f"Claude ({self.model})"
    
    async def generate_response(self, prompt: str, conversation_history: Optional[List[Dict]] = None, user_token: Optional[str] = None) -> str:
        effective_key = self.get_effective_key(user_token)
        if not effective_key:
            return "❌ Claude is not configured. Please set your API key with /settoken."
        
        try:
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    role = "assistant" if msg["role"] == "assistant" else "user"
                    messages.append({"role": role, "content": msg["content"]})
            
            messages.append({"role": "user", "content": prompt})
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "x-api-key": effective_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 2000
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Claude API error: {e}")
            if e.response.status_code == 401:
                return "❌ Invalid API key. Please update your token with /settoken."
            return f"❌ Claude API error: {e.response.status_code}"
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return f"❌ Error: {str(e)}"


class GrokService(AIService):
    """xAI Grok service"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "grok-beta", user_id: Optional[int] = None):
        super().__init__(api_key or os.getenv("XAI_API_KEY"), user_id)
        self.model = model
        self.base_url = "https://api.x.ai/v1/chat/completions"
    
    def is_available(self, user_token: Optional[str] = None) -> bool:
        return bool(self.get_effective_key(user_token))
    
    @property
    def name(self) -> str:
        return f"Grok ({self.model})"
    
    async def generate_response(self, prompt: str, conversation_history: Optional[List[Dict]] = None, user_token: Optional[str] = None) -> str:
        effective_key = self.get_effective_key(user_token)
        if not effective_key:
            return "❌ Grok is not configured. Please set your API key with /settoken."
        
        try:
            messages = conversation_history or []
            messages.append({"role": "user", "content": prompt})
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {effective_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 2000,
                        "temperature": 0.7
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Grok API error: {e}")
            if e.response.status_code == 401:
                return "❌ Invalid API key. Please update your token with /settoken."
            return f"❌ Grok API error: {e.response.status_code}"
        except Exception as e:
            logger.error(f"Grok error: {e}")
            return f"❌ Error: {str(e)}"


class CustomLLMService(AIService):
    """Custom LLM service with OpenAI-compatible API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = "custom-model", user_id: Optional[int] = None):
        super().__init__(api_key or os.getenv("CUSTOM_LLM_API_KEY"), user_id)
        self.base_url = base_url or os.getenv("CUSTOM_LLM_BASE_URL", "http://localhost:11434/v1/chat/completions")
        self.model = model or os.getenv("CUSTOM_LLM_MODEL", "llama3")
    
    def is_available(self, user_token: Optional[str] = None) -> bool:
        return bool(self.base_url)
    
    @property
    def name(self) -> str:
        return f"Custom LLM ({self.model})"
    
    async def generate_response(self, prompt: str, conversation_history: Optional[List[Dict]] = None, user_token: Optional[str] = None) -> str:
        if not self.is_available():
            return "❌ Custom LLM is not configured. Please set CUSTOM_LLM_BASE_URL."
        
        try:
            messages = conversation_history or []
            messages.append({"role": "user", "content": prompt})
            
            headers = {"Content-Type": "application/json"}
            effective_key = self.get_effective_key(user_token)
            if effective_key:
                headers["Authorization"] = f"Bearer {effective_key}"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 2000,
                        "temperature": 0.7
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Handle different response formats
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                elif "response" in data:
                    return data["response"]
                else:
                    return str(data)
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Custom LLM API error: {e}")
            return f"❌ Custom LLM API error: {e.response.status_code}"
        except Exception as e:
            logger.error(f"Custom LLM error: {e}")
            return f"❌ Error: {str(e)}"


class AIServiceManager:
    """Manager for all AI services"""
    
    def __init__(self):
        self.services = {
            "chatgpt": ChatGPTService(),
            "gemini": GeminiService(),
            "claude": ClaudeService(),
            "grok": GrokService(),
            "custom": CustomLLMService()
        }
        self.default_service = os.getenv("DEFAULT_AI_SERVICE", "chatgpt")
        
        # Updated model list for late 2025
        self.available_models = {
            "chatgpt": [
                "gpt-5",           # Top-tier, complex reasoning
                "gpt-5-mini",      # Balanced performance and speed
                "gpt-4.1",         # Successor to GPT-4 Turbo
                "gpt-4o",          # Still a strong, fast multimodal option
                "gpt-4o-mini"      # Excellent for fast, scalable tasks
                # "gpt-4-turbo" and "gpt-3.5-turbo" are now deprecated or legacy
            ],
            "gemini": [
                "gemini-2.5-pro",  # The new high-end, flagship model
                "gemini-2.5-flash" # The new fast, cost-effective model
                # "gemini-1.5-pro", "gemini-1.5-flash", and "gemini-pro" (1.0)
                # are all superseded by the 2.5 series
            ],
            "claude": [
                "claude-opus-4.1",     # Top-tier reasoning (replaces 3.0 Opus)
                "claude-sonnet-4.5",   # Main workhorse model (replaces 3.5 Sonnet)
                "claude-haiku-4.5"     # Fastest, most compact model
                # The Claude 3.x series is now legacy
            ],
            "grok": [
                "grok-4",              # Top-tier model from xAI
                "grok-4-fast",         # Faster, more economical version
                "grok-code-fast-1"     # Specialized for coding tasks
                # "grok-beta" and "grok-vision-beta" are very old demo names
            ],
            "custom": [
                # Note: These are model families. The exact ID depends on your provider
                # (e.g., Ollama, Groq, Replicate, or Hugging Face)
                "llama-4-scout",       # Meta's latest generation
                "llama-3.3-70b",       # Most advanced of the Llama 3 series
                "magistral-medium",    # Mistral's latest proprietary model
                "devstral-small"       # Mistral's latest open-weight code model
            ]
        }
    
    def get_service(self, service_name: str, model: Optional[str] = None, user_id: Optional[int] = None) -> Optional[AIService]:
        """Get AI service by name, optionally with custom model"""
        service_class_map = {
            "chatgpt": ChatGPTService,
            "gemini": GeminiService,
            "claude": ClaudeService,
            "grok": GrokService,
            "custom": CustomLLMService
        }
        
        service_class = service_class_map.get(service_name.lower())
        if not service_class:
            return None
        
        # Create instance with custom model if provided
        if model:
            return service_class(model=model, user_id=user_id)
        return service_class(user_id=user_id)
    
    def get_default_service(self) -> AIService:
        """Get the default AI service"""
        return self.services.get(self.default_service, self.services["chatgpt"])
    
    def get_available_services(self, user_token_manager=None, user_id: Optional[int] = None) -> List[tuple[str, AIService]]:
        """Get list of available (configured) services for a user"""
        available = []
        for name, service in self.services.items():
            # Check if service is available with env vars
            if service.is_available():
                available.append((name, service))
            # Or check if user has a token
            elif user_token_manager and user_id and user_token_manager.has_token(user_id, name):
                available.append((name, service))
        return available
    
    def get_all_services(self) -> Dict[str, AIService]:
        """Get all services"""
        return self.services
    
    def get_models_for_provider(self, provider: str) -> List[str]:
        """Get available models for a provider"""
        return self.available_models.get(provider, [])
