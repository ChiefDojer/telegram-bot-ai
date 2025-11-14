"""
User Token Management
Stores user-specific API tokens securely in memory.
NOTE: For production, use Redis or encrypted database storage.
"""
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class UserTokenManager:
    """
    Manages user-specific API tokens.
    
    IMPORTANT SECURITY NOTES:
    - Tokens are stored in memory and lost on restart
    - For production: Use Redis with encryption or secure database
    - Tokens are NOT sent to any server except the AI provider APIs
    - Each user's tokens are isolated and never shared
    """
    
    def __init__(self):
        # Structure: {user_id: {provider: {"token": str, "set_at": datetime, "model": str}}}
        self._user_tokens: Dict[int, Dict[str, Dict]] = {}
        self._user_preferences: Dict[int, Dict] = {}
    
    def set_token(self, user_id: int, provider: str, token: str, model: Optional[str] = None):
        """Store a user's API token for a specific provider"""
        if user_id not in self._user_tokens:
            self._user_tokens[user_id] = {}
        
        self._user_tokens[user_id][provider] = {
            "token": token,
            "set_at": datetime.now(),
            "model": model
        }
        logger.info(f"Token set for user {user_id}, provider {provider}")
    
    def get_token(self, user_id: int, provider: str) -> Optional[str]:
        """Retrieve a user's API token for a specific provider"""
        if user_id not in self._user_tokens:
            return None
        
        provider_data = self._user_tokens[user_id].get(provider)
        if provider_data:
            return provider_data.get("token")
        return None
    
    def remove_token(self, user_id: int, provider: str) -> bool:
        """Remove a user's API token for a specific provider"""
        if user_id in self._user_tokens and provider in self._user_tokens[user_id]:
            del self._user_tokens[user_id][provider]
            logger.info(f"Token removed for user {user_id}, provider {provider}")
            return True
        return False
    
    def get_user_providers(self, user_id: int) -> list[str]:
        """Get list of providers for which user has tokens"""
        if user_id not in self._user_tokens:
            return []
        return list(self._user_tokens[user_id].keys())
    
    def has_token(self, user_id: int, provider: str) -> bool:
        """Check if user has a token for the provider"""
        return self.get_token(user_id, provider) is not None
    
    def get_model(self, user_id: int, provider: str) -> Optional[str]:
        """Get user's preferred model for a provider"""
        if user_id not in self._user_tokens:
            return None
        
        provider_data = self._user_tokens[user_id].get(provider)
        if provider_data:
            return provider_data.get("model")
        return None
    
    def set_model(self, user_id: int, provider: str, model: str):
        """Set user's preferred model for a provider"""
        if user_id in self._user_tokens and provider in self._user_tokens[user_id]:
            self._user_tokens[user_id][provider]["model"] = model
    
    def set_preferred_provider(self, user_id: int, provider: str):
        """Set user's preferred AI provider"""
        if user_id not in self._user_preferences:
            self._user_preferences[user_id] = {}
        self._user_preferences[user_id]["provider"] = provider
    
    def get_preferred_provider(self, user_id: int) -> Optional[str]:
        """Get user's preferred AI provider"""
        if user_id in self._user_preferences:
            return self._user_preferences[user_id].get("provider")
        return None
    
    def clear_user_data(self, user_id: int):
        """Clear all data for a user"""
        if user_id in self._user_tokens:
            del self._user_tokens[user_id]
        if user_id in self._user_preferences:
            del self._user_preferences[user_id]
        logger.info(f"All data cleared for user {user_id}")
    
    def get_user_config(self, user_id: int) -> Dict:
        """Get complete configuration for a user"""
        config = {
            "preferred_provider": self.get_preferred_provider(user_id),
            "configured_providers": []
        }
        
        if user_id in self._user_tokens:
            for provider, data in self._user_tokens[user_id].items():
                config["configured_providers"].append({
                    "provider": provider,
                    "model": data.get("model"),
                    "set_at": data.get("set_at").strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return config


# Global instance
user_token_manager = UserTokenManager()
