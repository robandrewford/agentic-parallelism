"""Base tool abstraction for agent tools."""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Abstract base class for agent tools."""
    
    def __init__(self, name: str, description: str):
        """Initialize the tool with name and description."""
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the given arguments."""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema for the LLM."""
        return {
            "name": self.name,
            "description": self.description,
        }
