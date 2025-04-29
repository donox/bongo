import unittest
import argparse
import sys
import os
# Add the project root directory to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_base import BaseLEDTest

class LEDTestRunner:
    def __init__(self):
        self.test_suite = unittest.TestSuite()
        
    def add_test(self, test_class, test_name, led_id):
        """Add a specific test to the test suite"""
        test = test_class(test_name)
        test.led_id = led_id
        self.test_suite.addTest(test)
        
    def run_tests(self):
        """Run all tests in the suite"""
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(self.test_suite)

def main():
    parser = argparse.ArgumentParser(description='Run LED tests')
    parser.add_argument('--leds', nargs='+', type=int, help='LED IDs to test')
    parser.add_argument('--tests', nargs='+', choices=['on_off', 'fade'], help='Tests to run')
    args = parser.parse_args()
    
    if not args.leds:
        print("Please specify at least one LED ID to test")
        return
        
    if not args.tests:
        print("Please specify at least one test to run")
        return

        
    runner = LEDTestRunner()
    
    for led_id in args.leds:
        for test_name in args.tests:
            if test_name == 'on_off':
                runner.add_test(BaseLEDTest, 'test_led_on_off', led_id)
            elif test_name == 'fade':
                runner.add_test(BaseLEDTest, 'test_led_fade', led_id)
                
    runner.run_tests()

if __name__ == '__main__':
    main() 