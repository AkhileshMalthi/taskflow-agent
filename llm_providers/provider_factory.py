from typing import Dict, List, Optional, Any, Type
import importlib
import pkgutil
import inspect
from .base_provider import LLMProvider

# Dictionary to store provider classes
_provider_classes: Dict[str, Type[LLMProvider]] = {}

def register_provider(provider_class: Type[LLMProvider]) -> None:
    """
    Register an LLM provider class.
    
    Args:
        provider_class: LLM provider class to register
    """
    provider_name = provider_class.get_provider_name().lower()
    _provider_classes[provider_name] = provider_class

def get_provider(provider_name: str, credentials: Dict[str, str]) -> Optional[LLMProvider]:
    """
    Get an LLM provider instance by name.
    
    Args:
        provider_name: Name of the provider
        credentials: Dictionary of credentials required by the provider
        
    Returns:
        An initialized LLM provider or None if not found
    """
    # Ensure provider classes are loaded
    _ensure_providers_loaded()
    
    # Get provider class (case-insensitive)
    provider_key = provider_name.lower()
    provider_class = _provider_classes.get(provider_key)
    
    if not provider_class:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    
    # Get required credentials
    required_creds = provider_class.get_required_credentials()
    
    # Check if all required credentials are provided
    missing_creds = [cred for cred in required_creds if cred not in credentials or not credentials[cred]]
    if missing_creds:
        raise ValueError(f"Missing required credentials for {provider_name}: {', '.join(missing_creds)}")
    
    # Initialize the provider with the specified credentials
    return provider_class(**{k: v for k, v in credentials.items() if k in required_creds})

def list_available_providers() -> List[str]:
    """
    Get a list of available LLM providers.
    
    Returns:
        List of provider names
    """
    # Ensure provider classes are loaded
    _ensure_providers_loaded()
    
    # Return sorted list of provider names
    return sorted([cls.get_provider_name() for cls in _provider_classes.values()])

def _ensure_providers_loaded() -> None:
    """
    Ensure all provider classes are loaded.
    This will dynamically import all modules in the llm_providers package.
    """
    # Only load once
    if _provider_classes:
        return
    
    # Import this package
    package = importlib.import_module(__package__)
    
    # Walk through all modules in the package
    for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
        # Skip packages
        if is_pkg:
            continue
        
        # Skip this file
        if name == __name__:
            continue
        
        # Import the module
        module = importlib.import_module(name)
        
        # Find all LLMProvider subclasses in the module
        for item_name, item in module.__dict__.items():
            if (inspect.isclass(item) and 
                issubclass(item, LLMProvider) and 
                item != LLMProvider and
                hasattr(item, 'get_provider_name')):
                register_provider(item)

# Register built-in providers
from .groq_provider import GroqProvider
register_provider(GroqProvider)
