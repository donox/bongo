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

def get_controllers():
    controllers = []
    addresses = PCA9685_ADDRESSES
    
    for address in addresses:
        controllers.append(MockPCA9685(address=address))
        logger.info(f"Mock PCA9685 at address 0x{address:02x} initialized")
    
    return controllers