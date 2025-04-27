#!/usr/bin/env python3
import sys
import os
# Add the project root directory to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from logging_setup import logger
import os
from typing import List, Tuple, Optional, Dict, Any
import threading
from led_control.led_management import LED, LEDMatrix
from led_control.led_visualizer import LEDVisualizer
from constants import DEFAULT_COLS, DEFAULT_ROWS


# Determine if we're running on actual hardware
try:
    # Try to import RPi.GPIO as a test
    import RPi.GPIO as GPIO
    ON_HARDWARE = True
    logger.info("Running on actual Raspberry Pi hardware")
except (ImportError, RuntimeError):  
    ON_HARDWARE = False
    logger.info("Running in development mode with mock hardware")

# Import the appropriate hardware module
if ON_HARDWARE:
    from hardware.real_hardware import get_controllers
else:
    from hardware.mock_hardware import get_controllers

def run_demo_sequence(matrix: LEDMatrix):
    """Run the LED demo sequence"""
    # Turn all LEDs off
    matrix.all_off()
    
    # Blink each LED in sequence
    print("Blinking each LED in sequence...")
    matrix.blink_sequence(delay=1)  # .1 second delay (1 time unit)
    
    # Turn on all LEDs in the first row
    print("Turning on first row...")
    matrix.set_row(0)
    time.sleep(1)
    
    # Turn on all LEDs in the first column
    print("Turning on first column...")
    matrix.all_off()
    matrix.set_column(0)
    time.sleep(1)
    
    # Turn all LEDs off
    matrix.all_off()

def main():
    logger.info("Initializing controllers...")
    controllers = get_controllers()
    
    if not controllers:
        logger.error("No controllers found. Exiting.")
        return
    
    # Create a 6x9 LED matrix (54 LEDs total)
    matrix = LEDMatrix(DEFAULT_COLS, DEFAULT_ROWS, controllers)
    
    # Create and start the visualizer
    visualizer = LEDVisualizer(matrix)
    
    # Run the demo sequence in a separate thread
    demo_thread = threading.Thread(target=run_demo_sequence, args=(matrix,), daemon=True)
    demo_thread.start()
    
    # Run the visualizer (this will block until window is closed)
    visualizer.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
