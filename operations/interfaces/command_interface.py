from typing import Dict, List, Any, Optional
from ..commands.base import Command
from ..commands.led_commands import OnCommand, OffCommand, FadeCommand, PatternCommand

class CommandInterface:
    """Interface for handling LED operation commands"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.context: Dict[str, Any] = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register the default set of commands"""
        self.register_command(OnCommand())
        self.register_command(OffCommand())
        self.register_command(FadeCommand())
        self.register_command(PatternCommand())
    
    def register_command(self, command: Command):
        """Register a new command"""
        self.commands[command.name] = command
    
    def set_context(self, key: str, value: Any):
        """Set a value in the execution context"""
        self.context[key] = value
    
    def get_context(self, key: str) -> Optional[Any]:
        """Get a value from the execution context"""
        return self.context.get(key)
    
    def execute_command(self, command_line: str) -> bool:
        """
        Execute a command line
        
        Args:
            command_line: The command line to execute
            
        Returns:
            bool: True if command executed successfully
        """
        parts = command_line.strip().split()
        if not parts:
            return False
            
        command_name = parts[0].lower()
        args = parts[1:]
        
        command = self.commands.get(command_name)
        if not command:
            print(f"Unknown command: {command_name}")
            return False
            
        return command.execute(args, self.context)
    
    def get_help(self) -> str:
        """Get help text for all commands"""
        help_text = "Available commands:\n"
        for command in self.commands.values():
            help_text += f"  {command.help()}\n"
        return help_text 