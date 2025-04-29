from abc import ABC, abstractmethod
from typing import List, Dict, Any
import time
import threading

class Pattern(ABC):
    """Base class for all LED patterns"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._running = False
        self._paused = False
        self._thread = None
    
    @abstractmethod
    def execute(self, led_manager, args: List[str]) -> bool:
        """
        Execute the pattern
        
        Args:
            led_manager: LED manager instance
            args: Pattern arguments
            
        Returns:
            bool: True if pattern started successfully
        """
        pass
    
    def stop(self):
        """Stop the pattern"""
        self._running = False
        if self._thread:
            self._thread.join()
            self._thread = None
    
    def pause(self):
        """Pause the pattern"""
        self._paused = True
    
    def resume(self):
        """Resume the pattern"""
        self._paused = False
    
    def is_running(self) -> bool:
        """Check if pattern is running"""
        return self._running
    
    def is_paused(self) -> bool:
        """Check if pattern is paused"""
        return self._paused
    
    def _wait_if_paused(self):
        """Wait if pattern is paused"""
        while self._paused and self._running:
            time.sleep(0.1)
    
    def _run_in_thread(self, func, *args, **kwargs):
        """Run a function in a separate thread"""
        self._running = True
        self._thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        self._thread.daemon = True
        self._thread.start() 