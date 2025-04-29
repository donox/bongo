from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Command(ABC):
    """Base class for all LED operations commands"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, args: List[str], context: Dict[str, Any]) -> bool:
        """
        Execute the command
        
        Args:
            args: Command arguments
            context: Execution context (hardware, led_manager, etc.)
            
        Returns:
            bool: True if command executed successfully
        """
        pass
    
    def help(self) -> str:
        """Get help text for this command"""
        return f"{self.name}: {self.description}" 