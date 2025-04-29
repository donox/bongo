import sys
from typing import Optional
from hardware.mock_hardware import MockHardware
from led_control.led_management import LEDManager
from .interfaces.command_interface import CommandInterface

def main():
    # Initialize hardware and LED manager
    hardware = MockHardware()
    led_manager = LEDManager(hardware)
    
    # Create command interface
    interface = CommandInterface()
    interface.set_context('led_manager', led_manager)
    
    print("LED Operations CLI")
    print("Type 'help' for available commands")
    print("Type 'exit' to quit")
    
    while True:
        try:
            command_line = input("> ").strip()
            
            if command_line.lower() == 'exit':
                break
            elif command_line.lower() == 'help':
                print(interface.get_help())
            else:
                interface.execute_command(command_line)
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main() 