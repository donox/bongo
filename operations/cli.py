import sys
import argparse
from typing import Optional
from hardware.mock_hardware import MockHardware
from led_control.led_management import LEDManager
from .interfaces.command_interface import CommandInterface
from .interfaces.remote_interface import RemoteInterface

def main():
    parser = argparse.ArgumentParser(description='LED Operations CLI')
    parser.add_argument('--remote', action='store_true', help='Use remote hardware')
    parser.add_argument('--host', help='Remote hostname or IP')
    parser.add_argument('--user', help='Remote username')
    parser.add_argument('--password', help='Remote password')
    parser.add_argument('--key', help='Path to SSH private key')
    args = parser.parse_args()
    
    if args.remote:
        if not all([args.host, args.user]):
            print("Error: --host and --user are required for remote mode")
            return
            
        # Use remote interface
        with RemoteInterface(
            hostname=args.host,
            username=args.user,
            password=args.password,
            key_filename=args.key
        ) as remote:
            if not remote.connect():
                return
                
            print("Connected to remote hardware")
            print("Type 'help' for available commands")
            print("Type 'exit' to quit")
            
            while True:
                try:
                    command_line = input("> ").strip()
                    
                    if command_line.lower() == 'exit':
                        break
                    elif command_line.lower() == 'help':
                        print(remote.command_interface.get_help())
                    else:
                        remote.execute_command(command_line)
                        
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
                except Exception as e:
                    print(f"Error: {e}")
    else:
        # Use local mock hardware
        hardware = MockHardware()
        led_manager = LEDManager(hardware)
        
        # Create command interface
        interface = CommandInterface()
        interface.set_context('led_manager', led_manager)
        
        print("Using local mock hardware")
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