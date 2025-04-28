# hardware/mock_hardware.py
import logging
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
    """Mock hardware controller for testing LED functionality"""
    
    def __init__(self):
        """Initialize the mock hardware with a single controller"""
        self.system = HardwareSystem()
        self.controller = self.system.controllers[0]  # Use the first controller
        self.channels = self.controller.channels
    
    def set_channel(self, channel: int, value: int):
        """
        Set the value of a channel
        
        Args:
            channel: Channel number (0-15)
            value: Duty cycle value (0-65535)
        """
        if 0 <= channel < len(self.channels):
            self.channels[channel].duty_cycle = value
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