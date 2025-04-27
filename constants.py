# constants.py
"""Constants used throughout the project."""

# Time constants
TIME_UNIT = 0.1  # Each time unit is 0.1 seconds

# Hardware constants
MAX_CONTROLLERS = 4
CHANNELS_PER_CONTROLLER = 16
MAX_BRIGHTNESS = 100

# PCA9685 addresses
PCA9685_ADDRESSES = [0x40, 0x41, 0x42, 0x43]

# LED Matrix configuration
DEFAULT_ROWS = 6
DEFAULT_COLS = 9