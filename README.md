# Bongo LED Control System

A Python-based LED control system for managing LED matrices and individual LEDs. The system supports both real hardware (PCA9685) and mock hardware for testing.

## Features

- LED matrix management with row/column operations
- Individual LED control with brightness adjustment
- Scheduled LED tasks with timing control
- Mock hardware for testing
- Comprehensive test suite

## Project Structure

```
.
├── hardware/
│   ├── mock_hardware.py    # Mock hardware implementation
│   └── real_hardware.py    # Real hardware implementation
├── led_control/
│   └── led_management.py   # Core LED management system
└── tests/
    ├── test_base.py        # Base test class
    └── test_runner.py      # Test runner
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
python tests/test_runner.py --leds <led_ids> --tests <test_types>
```

## Development

- The system uses a modular design with separate classes for LED, LEDMatrix, and LEDManager
- Mock hardware is provided for testing without physical hardware
- Tests can be run for individual LEDs or the entire matrix

## License

MIT License 