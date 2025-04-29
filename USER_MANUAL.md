# Bongo LED Control System User Manual

## Overview

The Bongo LED Control System is a Python-based application that allows you to control LED matrices either locally (using mock hardware) or remotely (using real hardware). The system provides a command-line interface for controlling individual LEDs, creating patterns, and managing LED sequences.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/donox/bongo.git
cd bongo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the System

### Local Mode (Mock Hardware)

To run the system with mock hardware (displays LED states in a Tkinter window):

```bash
python3 -m operations.cli
```

### Remote Mode (Real Hardware)

To run the system with real hardware connected via SSH:

```bash
python3 -m operations.cli --remote --host <hostname> --user <username> [--password <password> | --key <key_file>]
```

Example:
```bash
# Using password authentication
python3 -m operations.cli --remote --host 192.168.1.100 --user pi --password raspberry

# Using SSH key authentication
python3 -m operations.cli --remote --host 192.168.1.100 --user pi --key ~/.ssh/id_rsa
```

## Available Commands

### Basic LED Control

1. Turn on one or more LEDs:
```
on <led_id> [led_id2 ...]
```
Example: `on 0 1 2` turns on LEDs 0, 1, and 2

2. Turn off one or more LEDs:
```
off <led_id> [led_id2 ...]
```
Example: `off 0 1 2` turns off LEDs 0, 1, and 2

3. Fade one or more LEDs:
```
fade <led_id> <duration> [led_id2 duration2 ...]
```
Example: `fade 0 0.5` fades LED 0 over 0.5 seconds

4. Set a pattern:
```
pattern <pattern_name>
```
Example: `pattern wave` sets the wave pattern (if implemented)

### Pattern Commands

The system supports several predefined patterns that can be used to create complex LED sequences:

1. Wave Pattern:
```
pattern wave [direction] [speed]
```
- `direction`: 'left', 'right', 'up', 'down' (default: 'right')
- `speed`: float value in seconds (default: 0.5)
Example: `pattern wave left 0.3` creates a left-moving wave at 0.3s speed

2. Blink Pattern:
```
pattern blink <led_ids> [duration] [count]
```
- `led_ids`: space-separated list of LED IDs
- `duration`: blink duration in seconds (default: 0.5)
- `count`: number of blinks (default: 3)
Example: `pattern blink 0 1 2 0.2 5` blinks LEDs 0,1,2 for 0.2s, 5 times

3. Chase Pattern:
```
pattern chase <start_led> <end_led> [direction] [speed]
```
- `start_led`: first LED in sequence
- `end_led`: last LED in sequence
- `direction`: 'forward' or 'reverse' (default: 'forward')
- `speed`: float value in seconds (default: 0.3)
Example: `pattern chase 0 5 reverse 0.2` chases LEDs 0-5 in reverse at 0.2s speed

4. Rainbow Pattern:
```
pattern rainbow [speed] [brightness]
```
- `speed`: cycle speed in seconds (default: 1.0)
- `brightness`: 0.0 to 1.0 (default: 1.0)
Example: `pattern rainbow 0.5 0.8` creates a rainbow effect at 0.5s speed, 80% brightness

5. Custom Pattern:
```
pattern custom <pattern_file>
```
- `pattern_file`: path to a JSON file containing pattern definition
Example: `pattern custom patterns/my_pattern.json`

Pattern File Format (JSON):
```json
{
    "name": "custom_pattern",
    "steps": [
        {
            "leds": [0, 1, 2],
            "brightness": 1.0,
            "duration": 0.5
        },
        {
            "leds": [3, 4, 5],
            "brightness": 0.5,
            "duration": 0.3
        }
    ]
}
```

### Pattern Control Commands

1. Stop Pattern:
```
pattern stop
```
Stops the currently running pattern

2. Pause Pattern:
```
pattern pause
```
Pauses the current pattern

3. Resume Pattern:
```
pattern resume
```
Resumes a paused pattern

4. List Patterns:
```
pattern list
```
Shows all available patterns

### System Commands

- `help` - Display available commands
- `exit` - Exit the program

## Examples

### Example 1: Basic LED Control
```
> on 0 1 2
> fade 3 0.5
> off 0 1 2 3
```

### Example 2: Creating a Sequence
```
> on 0
> fade 1 0.3
> on 2
> fade 3 0.3
> off 0 1 2 3
```

### Example 3: Remote Control
```bash
# Connect to remote hardware
python3 -m operations.cli --remote --host 192.168.1.100 --user pi --key ~/.ssh/id_rsa

# Once connected, use commands as normal
> on 0 1 2
> fade 3 0.5
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify the hostname/IP is correct
   - Check SSH credentials
   - Ensure the remote server is running and accessible

2. **Command Not Working**
   - Check command syntax
   - Verify LED IDs are valid
   - Ensure proper permissions on remote system

3. **Mock Hardware Not Displaying**
   - Ensure Tkinter is installed
   - Check for any error messages in the console

### Getting Help

- Use the `help` command in the CLI for available commands
- Check the GitHub repository for issues and updates
- Review the test files for examples of command usage

## Development

### Running Tests

To run the test suite:
```bash
python3 -m unittest discover tests
```

### Adding New Commands

1. Create a new command class in `operations/commands/`
2. Inherit from the base `Command` class
3. Implement the `execute` method
4. Register the command in `CommandInterface`

## License

MIT License - See LICENSE file for details 