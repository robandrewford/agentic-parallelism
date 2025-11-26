"""Base LLM abstraction."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseLLM(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model_name: str, **kwargs):
        """Initialize the LLM with model name and configuration."""
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    def invoke(self, messages: list, **kwargs) -> Any:
        """Invoke the LLM with a list of messages."""
        pass
    
    @abstractmethod
    def bind_tools(self, tools: list) -> "BaseLLM":
        """Bind tools to the LLM for function calling."""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """Get the LLM configuration."""
        return {
            "model_name": self.model_name,
            **self.config
        }
