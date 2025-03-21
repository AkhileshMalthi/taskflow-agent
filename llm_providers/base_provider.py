from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def get_llm(self, model_name: str, **kwargs) -> Any:
        """
        Initialize and return an LLM instance that can be used with CrewAI agents.
        
        Args:
            model_name: Name of the model to use
            **kwargs: Additional model-specific parameters
            
        Returns:
            LLM instance compatible with CrewAI
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """
        Get a list of available models for this provider.
        
        Returns:
            List of model names
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_provider_name(cls) -> str:
        """
        Get the name of this provider for display and selection.
        
        Returns:
            Provider name
        """
        pass
    
    @classmethod
    def get_required_credentials(cls) -> List[str]:
        """
        Get a list of credential keys required by this provider.
        
        Returns:
            List of required credential keys
        """
        return ["api_key"]
