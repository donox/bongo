import unittest
import time
from led_control.led_management import LEDManager
from hardware.mock_hardware import MockHardware

class BaseLEDTest(unittest.TestCase):
    def setUp(self):
        self.hardware = MockHardware()
        self.led_manager = LEDManager(self.hardware)
        
    def tearDown(self):
        # Turn off all LEDs after each test
        for led_id in range(self.led_manager.num_leds):
            self.led_manager.set_led(led_id, 0)
            
    def assert_led_state(self, led_id, expected_state):
        """Assert that an LED is in the expected state"""
        actual_state = self.led_manager.get_led_state(led_id)
        self.assertEqual(actual_state, expected_state)
        
    def fade_led(self, led_id, start_brightness, end_brightness, duration=1.0, steps=10):
        """Gradually change LED brightness over time"""
        step_duration = duration / steps
        brightness_step = (end_brightness - start_brightness) / steps
        
        for i in range(steps + 1):
            brightness = start_brightness + (brightness_step * i)
            self.led_manager.set_led(led_id, brightness)
            time.sleep(step_duration)
            
    def test_led_on_off(self, led_id):
        """Test basic on/off functionality for an LED"""
        # Test turning on
        self.led_manager.set_led(led_id, 1.0)
        self.assert_led_state(led_id, 1.0)
        
        # Test turning off
        self.led_manager.set_led(led_id, 0.0)
        self.assert_led_state(led_id, 0.0)
        
    def test_led_fade(self, led_id):
        """Test fading functionality for an LED"""
        # Test fade in
        self.fade_led(led_id, 0.0, 1.0, duration=0.5)
        self.assert_led_state(led_id, 1.0)
        
        # Test fade out
        self.fade_led(led_id, 1.0, 0.0, duration=0.5)
        self.assert_led_state(led_id, 0.0) 