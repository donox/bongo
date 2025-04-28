# LED Testing Framework

This testing framework provides a way to test individual LEDs in the Bongo system. It supports both basic on/off testing and fade testing.

## Available Tests

1. `on_off`: Tests basic LED functionality by turning the LED on and off
2. `fade`: Tests LED fading functionality by gradually increasing and decreasing brightness

## Usage

Run tests using the test runner script:

```bash
python test_runner.py --leds <led_ids> --tests <test_types>
```

### Examples

Test LED 0 with on/off functionality:
```bash
python test_runner.py --leds 0 --tests on_off
```

Test LEDs 1 and 2 with fade functionality:
```bash
python test_runner.py --leds 1 2 --tests fade
```

Test LED 0 with both on/off and fade functionality:
```bash
python test_runner.py --leds 0 --tests on_off fade
```

## Adding New Tests

To add new tests:
1. Add new test methods to the `BaseLEDTest` class in `test_base.py`
2. Add the new test type to the choices in the argument parser in `test_runner.py`
3. Add the test to the main function in `test_runner.py` 