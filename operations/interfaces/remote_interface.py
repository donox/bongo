import paramiko
import time
from typing import Optional, Dict, Any
from ..interfaces.command_interface import CommandInterface

class RemoteInterface:
    """Interface for remote hardware control via SSH"""
    
    def __init__(self, hostname: str, username: str, password: Optional[str] = None, key_filename: Optional[str] = None):
        """
        Initialize remote interface
        
        Args:
            hostname: SSH server hostname or IP
            username: SSH username
            password: SSH password (optional if using key)
            key_filename: Path to SSH private key file (optional if using password)
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.client: Optional[paramiko.SSHClient] = None
        self.command_interface: Optional[CommandInterface] = None
    
    def connect(self) -> bool:
        """
        Connect to the remote server
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect using either password or key
            if self.key_filename:
                self.client.connect(
                    hostname=self.hostname,
                    username=self.username,
                    key_filename=self.key_filename
                )
            else:
                self.client.connect(
                    hostname=self.hostname,
                    username=self.username,
                    password=self.password
                )
            
            # Initialize command interface on remote
            self._initialize_remote_interface()
            return True
            
        except Exception as e:
            print(f"Error connecting to {self.hostname}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the remote server"""
        if self.client:
            self.client.close()
            self.client = None
    
    def _initialize_remote_interface(self):
        """Initialize the command interface on the remote server"""
        if not self.client:
            return
            
        # Create a command interface instance on the remote
        self.command_interface = CommandInterface()
        
        # Execute Python code to set up the interface
        setup_code = """
import sys
from led_control.led_management import LEDManager
from hardware.real_hardware import RealHardware

# Initialize hardware and LED manager
hardware = RealHardware()
led_manager = LEDManager(hardware)

# Set up command interface
from operations.interfaces.command_interface import CommandInterface
interface = CommandInterface()
interface.set_context('led_manager', led_manager)
"""
        self.client.exec_command(f"python3 -c '{setup_code}'")
    
    def execute_command(self, command_line: str) -> bool:
        """
        Execute a command on the remote server
        
        Args:
            command_line: The command to execute
            
        Returns:
            bool: True if command executed successfully
        """
        if not self.client:
            print("Not connected to remote server")
            return False
            
        try:
            # Execute the command on the remote
            stdin, stdout, stderr = self.client.exec_command(f"python3 -c 'from operations.cli import main; main()'")
            
            # Send the command
            stdin.write(f"{command_line}\n")
            stdin.flush()
            
            # Get the output
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            if error:
                print(f"Error: {error}")
                return False
                
            print(output)
            return True
            
        except Exception as e:
            print(f"Error executing command: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect() 