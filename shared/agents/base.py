"""Base agent abstraction."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAgent(ABC):
    """Abstract base class for agents."""
    
    def __init__(self, name: str, llm: Any, tools: List[Any] = None):
        """Initialize the agent with name, LLM, and tools."""
        self.name = name
        self.llm = llm
        self.tools = tools or []
    
    @abstractmethod
    def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """Execute the agent with the given query."""
        pass
    
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent."""
        self.tools.append(tool)
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": self.name,
            "tools": [tool.name if hasattr(tool, "name") else str(tool) for tool in self.tools],
        }
