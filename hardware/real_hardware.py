# hardware/real_hardware.py
import board
import busio
from adafruit_pca9685 import PCA9685
from constants import PCA9685_ADDRESSES

def get_controllers():
    i2c = busio.I2C(board.SCL, board.SDA)
    controllers = []
    
    for address in PCA9685_ADDRESSES:
        try:
            pca = PCA9685(i2c, address=address)
            pca.frequency = 60
            controllers.append(pca)
        except Exception as e:
            print(f"Failed to initialize PCA9685 at address 0x{address:02x}: {e}")
    
    return controllers