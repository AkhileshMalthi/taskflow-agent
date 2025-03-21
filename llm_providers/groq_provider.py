from typing import Dict, List, Any
from langchain_groq import ChatGroq
from .base_provider import LLMProvider

class GroqProvider(LLMProvider):
    """LLM provider implementation for Groq."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # Define available models and their max context
        self.available_models = {
            "mixtral-8x7b-32768": {
                "display_name": "Mixtral 8x7B",
                "context_length": 32768
            },
            "llama3-70b-8192": {
                "display_name": "Llama 3 70B",
                "context_length": 8192
            },
            "llama3-8b-8192": {
                "display_name": "Llama 3 8B",
                "context_length": 8192
            },
            "gemma-7b-it": {
                "display_name": "Gemma 7B",
                "context_length": 8192
            }
        }
    
    def get_llm(self, model_name: str, **kwargs) -> Any:
        """
        Initialize and return a Groq LLM instance.
        
        Args:
            model_name: Name of the Groq model (without groq/ prefix)
            **kwargs: Additional parameters for the ChatGroq class
            
        Returns:
            ChatGroq instance
        """
        # Add 'groq/' prefix if not already present
        if not model_name.startswith("groq/"):
            full_model_name = f"groq/{model_name}"
        else:
            full_model_name = model_name
            model_name = model_name.replace("groq/", "")
        
        # Check if model exists
        if model_name not in self.available_models:
            raise ValueError(f"Model {model_name} not available for Groq provider")
        
        # Create and return the LLM
        return ChatGroq(
            model=full_model_name,
            api_key=self.api_key,
            **kwargs
        )
    
    def list_models(self) -> List[str]:
        """
        Get a list of available models for Groq.
        
        Returns:
            List of model names
        """
        return list(self.available_models.keys())
    
    def get_model_details(self) -> Dict[str, Dict]:
        """
        Get details about all available models.
        
        Returns:
            Dictionary mapping model names to their details
        """
        return self.available_models
    
    @classmethod
    def get_provider_name(cls) -> str:
        """Get the provider name."""
        return "Groq"
    
    @classmethod
    def get_required_credentials(cls) -> List[str]:
        """Get required credentials for Groq."""
        return ["api_key"]
