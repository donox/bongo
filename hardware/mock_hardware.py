# hardware/mock_hardware.py
import logging
import tkinter as tk
from tkinter import ttk
import threading
from constants import PCA9685_ADDRESSES, CHANNELS_PER_CONTROLLER

logger = logging.getLogger(__name__)

class MockPWMChannel:
    def __init__(self, channel_num, controller_address):
        self.channel_num = channel_num
        self.controller_address = controller_address
        self._duty_cycle = 0
    
    @property
    def duty_cycle(self):
        return self._duty_cycle
    
    @duty_cycle.setter
    def duty_cycle(self, value):
        self._duty_cycle = value
        state = "ON" if value > 0 else "OFF"
        logger.info(f"LED on controller 0x{self.controller_address:02x}, channel {self.channel_num} set to {state}")

class MockPCA9685:
    def __init__(self, i2c=None, address=0x40):
        self.address = address
        self.channels = [MockPWMChannel(i, address) for i in range(CHANNELS_PER_CONTROLLER)]
        self._frequency = 60
    
    @property
    def frequency(self):
        return self._frequency
    
    @frequency.setter
    def frequency(self, value):
        self._frequency = value

class HardwareSystem:
    """Represents the entire hardware system with multiple controllers"""
    
    def __init__(self):
        """Initialize the hardware system"""
        self.controllers = self._initialize_controllers()
    
    def _initialize_controllers(self):
        """Initialize all controllers in the system"""
        controllers = []
        addresses = PCA9685_ADDRESSES
        
        for address in addresses:
            controllers.append(MockPCA9685(address=address))
            logger.info(f"Mock PCA9685 at address 0x{address:02x} initialized")
        
        return controllers
    
    def get_controllers(self):
        """Get all controllers in the system"""
        return self.controllers

# For backward compatibility
def get_controllers():
    """Legacy function to get all controllers"""
    system = HardwareSystem()
    return system.get_controllers()

class MockHardware:
    """Mock hardware controller with Tkinter visualization"""
    
    def __init__(self):
        """Initialize the mock hardware with a single controller"""
        self.controller = MockPCA9685()
        self.channels = self.controller.channels
        self._root = None
        self._led_frames = []
        self._start_visualization()
    
    def _start_visualization(self):
        """Start the Tkinter visualization in a separate thread"""
        def run_visualization():
            self._root = tk.Tk()
            self._root.title("LED Matrix Visualization")
            
            # Create main frame
            main_frame = ttk.Frame(self._root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Create LED frames in a grid
            for i in range(4):  # 4x4 grid
                for j in range(4):
                    frame = ttk.Frame(main_frame, width=50, height=50, relief="solid", borderwidth=1)
                    frame.grid(row=i, column=j, padx=2, pady=2)
                    frame.grid_propagate(False)
                    
                    # Create LED indicator
                    led = ttk.Label(frame, text="●", font=("Arial", 24))
                    led.place(relx=0.5, rely=0.5, anchor="center")
                    led.configure(foreground="gray")
                    
                    self._led_frames.append((frame, led))
            
            # Start the Tkinter event loop
            self._root.mainloop()
        
        # Start visualization in a separate thread
        self._viz_thread = threading.Thread(target=run_visualization, daemon=True)
        self._viz_thread.start()
    
    def set_channel(self, channel: int, value: int):
        """
        Set the value of a channel
        
        Args:
            channel: Channel number (0-15)
            value: Duty cycle value (0-65535)
        """
        if 0 <= channel < len(self.channels):
            self.channels[channel].duty_cycle = value
            self._update_visualization(channel, value)
        else:
            logger.error(f"Invalid channel number: {channel}")
    
    def get_channel(self, channel: int) -> int:
        """
        Get the current value of a channel
        
        Args:
            channel: Channel number (0-15)
            
        Returns:
            Current duty cycle value (0-65535)
        """
        if 0 <= channel < len(self.channels):
            return self.channels[channel].duty_cycle
        else:
            logger.error(f"Invalid channel number: {channel}")
            return 0
    
    def _update_visualization(self, channel: int, value: int):
        """Update the LED visualization"""
        if not self._root or channel >= len(self._led_frames):
            return
            
        # Convert duty cycle to brightness (0-1)
        brightness = value / 65535.0
        
        # Update LED color based on brightness
        frame, led = self._led_frames[channel]
        if brightness > 0:
            # Convert brightness to color (gray to white)
            color = f"#{int(brightness * 255):02x}{int(brightness * 255):02x}{int(brightness * 255):02x}"
            led.configure(foreground=color)
        else:
            led.configure(foreground="gray")
        
        # Update the display
        self._root.update_idletasks()
    
    def __del__(self):
        """Clean up when the object is destroyed"""
        if self._root:
            self._root.quit()
            self._root.destroy()