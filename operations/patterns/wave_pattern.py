import time
from typing import List
from .pattern_base import Pattern

class WavePattern(Pattern):
    """Wave pattern that moves across the LED matrix"""
    
    def __init__(self):
        super().__init__("wave", "Create a wave effect moving across the LEDs")
    
    def execute(self, led_manager, args: List[str]) -> bool:
        """
        Execute the wave pattern
        
        Args:
            led_manager: LED manager instance
            args: Pattern arguments [direction, speed]
            
        Returns:
            bool: True if pattern started successfully
        """
        # Parse arguments
        direction = args[0] if args else 'right'
        speed = float(args[1]) if len(args) > 1 else 0.5
        
        # Validate direction
        if direction not in ['left', 'right', 'up', 'down']:
            print(f"Invalid direction: {direction}")
            return False
        
        # Start the pattern in a separate thread
        self._run_in_thread(self._wave_effect, led_manager, direction, speed)
        return True
    
    def _wave_effect(self, led_manager, direction: str, speed: float):
        """Run the wave effect"""
        try:
            while self._running:
                self._wait_if_paused()
                
                # Get the number of LEDs
                num_leds = led_manager.num_leds
                
                # Create wave effect
                for i in range(num_leds):
                    if not self._running:
                        break
                        
                    self._wait_if_paused()
                    
                    # Turn off all LEDs
                    for j in range(num_leds):
                        led_manager.set_led(j, 0.0)
                    
                    # Turn on current LED
                    led_manager.set_led(i, 1.0)
                    
                    # Wait for next step
                    time.sleep(speed)
                
        except Exception as e:
            print(f"Error in wave pattern: {e}")
        finally:
            # Turn off all LEDs when done
            for i in range(led_manager.num_leds):
                led_manager.set_led(i, 0.0) 