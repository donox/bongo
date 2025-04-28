from typing import List, Tuple, Optional, Dict, Any
import time
from logging_setup import logger
from constants import TIME_UNIT
import threading

class LED:
    """Base LED class that represents a single LED"""
    
    def __init__(self, led_id: int, controller=None, channel: int = 0):
        """
        Initialize an LED object
        
        Args:
            led_id: Unique identifier for this LED
            controller: Hardware controller object (PCA9685 or mock)
            channel: Channel number on the controller
        """
        self.led_id = led_id
        self.controller = controller
        self.channel = channel
        self._brightness = 0  # 0-100 scale
        logger.debug(f"LED {led_id} initialized on channel {channel}")
    
    @property
    def brightness(self) -> int:
        """Get current brightness level (0-100)"""
        return self._brightness
    
    @brightness.setter
    def brightness(self, value: int):
        """
        Set brightness level (0-100)
        
        Args:
            value: Brightness level from 0 (off) to 100 (full brightness)
        """
        # Clamp value between 0 and 100
        value = max(0, min(100, value))
        self._brightness = value
        
        # If we have a controller, set the duty cycle
        if self.controller:
            # Convert 0-100 to 0-0xFFFF (16-bit value for PCA9685)
            duty_cycle = int((value / 100.0) * 0xFFFF)
            controller_idx = self.led_id // 16
            channel_idx = self.led_id % 16
            
            try:
                self.controller.channels[channel_idx].duty_cycle = duty_cycle
                logger.debug(f"LED {self.led_id} brightness set to {value}%")
            except Exception as e:
                logger.error(f"Error setting brightness for LED {self.led_id}: {e}")
    
    def on(self, brightness: int = 100):
        """Turn LED on at specified brightness"""
        self.brightness = brightness
    
    def off(self):
        """Turn LED off"""
        self.brightness = 0
    
    def is_on(self) -> bool:
        """Check if LED is on (any brightness > 0)"""
        return self.brightness > 0
    
    def __str__(self) -> str:
        return f"LED(id={self.led_id}, brightness={self.brightness})"


class ScheduledTask:
    """Represents a scheduled task for one or more LEDs"""
    
    def __init__(self, task_id: int, leds: List[LED], start_time: int, duration: int, brightness: int = 100, restore_original: bool = True):
        """
        Initialize a scheduled task
        
        Args:
            task_id: Unique identifier for this task
            leds: List of LEDs to control
            start_time: Time to turn on (in time units from now)
            duration: How long to stay on (in time units)
            brightness: Brightness level (0-100)
            restore_original: Whether to restore original brightness after task completes
        """
        self.task_id = task_id
        self.leds = leds
        self.start_time = start_time
        self.duration = duration
        self.brightness = brightness
        self.restore_original = restore_original
        self.executed = False
        self.timer = None
        self.original_brightness = {led.led_id: led.brightness for led in leds}
        
    def schedule(self):
        """Schedule this task to execute"""
        self.timer = threading.Timer(self.start_time * TIME_UNIT, self.execute)
        self.timer.start()
        
    def execute(self):
        """Execute the task - turn on all LEDs at specified brightness"""
        if self.executed:
            return
        
        self.executed = True
        
        # Turn on all LEDs at specified brightness
        for led in self.leds:
            led.on(self.brightness)
        
        led_ids = [led.led_id for led in self.leds]
        logger.debug(f"Executed task {self.task_id} for LEDs {led_ids}")
        
        # Schedule turning off or restoring original brightness
        def restore():
            for led in self.leds:
                if self.restore_original and self.original_brightness[led.led_id] > 0:
                    led.brightness = self.original_brightness[led.led_id]
                else:
                    led.off()
            logger.debug(f"Completed task {self.task_id} for LEDs {led_ids}")
        
        threading.Timer(self.duration * TIME_UNIT, restore).start()
    
    def cancel(self) -> bool:
        """Cancel the task if it hasn't executed yet"""
        if self.executed:
            logger.warning(f"Task {self.task_id} already executed")
            return False
        
        if self.timer:
            self.timer.cancel()
        
        self.executed = True  # Mark as executed so it won't run
        led_ids = [led.led_id for led in self.leds]
        logger.debug(f"Cancelled task {self.task_id} for LEDs {led_ids}")
        return True


class LEDMatrix:
    """A matrix of LEDs arranged in rows and columns"""
    
    def __init__(self, rows: int, cols: int, controllers=None):
        """
        Initialize an LED matrix
        
        Args:
            rows: Number of rows in the matrix
            cols: Number of columns in the matrix
            controllers: List of hardware controllers
        """
        self.rows = rows
        self.cols = cols
        self.controllers = controllers
        self.leds: List[LED] = []
        self._scheduled_tasks: List[ScheduledTask] = []
        self._next_task_id = 0
        
        # Create all LEDs
        total_leds = rows * cols
        for i in range(total_leds):
            # Determine controller and channel
            if controllers:
                controller_idx = i // 16
                if controller_idx < len(controllers):
                    controller = controllers[controller_idx]
                else:
                    controller = None
                    logger.warning(f"Not enough controllers for LED {i}")
            else:
                controller = None
            
            self.leds.append(LED(i, controller, i % 16))
        
        logger.info(f"Created LED matrix with {rows} rows and {cols} columns ({total_leds} LEDs total)")
    
    def led_at(self, row: int, col: int) -> Optional[LED]:
        """
        Get the LED at a specific row and column
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            
        Returns:
            LED object or None if out of bounds
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            logger.error(f"Position ({row}, {col}) is out of bounds")
            return None
        
        index = row * self.cols + col
        return self.leds[index]
    
    def position_of(self, led_id: int) -> Tuple[int, int]:
        """
        Get the row and column of a specific LED
        
        Args:
            led_id: ID of the LED
            
        Returns:
            Tuple of (row, column)
        """
        if not (0 <= led_id < len(self.leds)):
            logger.error(f"LED ID {led_id} is out of bounds")
            return (-1, -1)
        
        row = led_id // self.cols
        col = led_id % self.cols
        return (row, col)
    
    def all_off(self):
        """Turn all LEDs off"""
        for led in self.leds:
            led.off()
        logger.debug("All LEDs turned off")
    
    def all_on(self, brightness: int = 100):
        """Turn all LEDs on at specified brightness"""
        for led in self.leds:
            led.on(brightness)
        logger.debug(f"All LEDs turned on at brightness {brightness}")
    
    def set_row(self, row: int, brightness: int = 100):
        """Turn on all LEDs in a specific row"""
        if not (0 <= row < self.rows):
            logger.error(f"Row {row} is out of bounds")
            return
        
        for col in range(self.cols):
            self.led_at(row, col).on(brightness)
        logger.debug(f"Row {row} turned on at brightness {brightness}")
    
    def set_column(self, col: int, brightness: int = 100):
        """Turn on all LEDs in a specific column"""
        if not (0 <= col < self.cols):
            logger.error(f"Column {col} is out of bounds")
            return
        
        for row in range(self.rows):
            self.led_at(row, col).on(brightness)
        logger.debug(f"Column {col} turned on at brightness {brightness}")
    
    def set_pattern(self, pattern: List[List[int]]):
        """
        Set a pattern of brightness values for the matrix
        
        Args:
            pattern: 2D list of brightness values (0-100)
        """
        for row in range(min(len(pattern), self.rows)):
            for col in range(min(len(pattern[row]), self.cols)):
                led = self.led_at(row, col)
                if led:
                    led.brightness = pattern[row][col]
        logger.debug("Pattern set on LED matrix")
    
    def blink_sequence(self, delay: int = 10):
        """Blink each LED in sequence with a delay between each"""
        self.all_off()
        for led in self.leds:
            led.on()
            time.sleep(delay * TIME_UNIT)
            led.off()
        logger.debug(f"Blink sequence completed with delay {delay}")
    
    def schedule_leds(self, led_ids: List[int], start_time: int, duration: int, brightness: int = 100, restore_original: bool = True) -> int:
        """
        Schedule multiple LEDs to turn on at the same time for a specific duration
        
        Args:
            led_ids: List of LED IDs to schedule
            start_time: Time to turn on (in time units from now)
            duration: How long to stay on (in time units)
            brightness: Brightness level (0-100)
            restore_original: Whether to restore original brightness after task completes
            
        Returns:
            task_id: ID of the scheduled task
        """
        # Get LED objects from IDs
        leds = [self.leds[led_id] for led_id in led_ids if 0 <= led_id < len(self.leds)]
        
        if not leds:
            logger.error("No valid LEDs to schedule")
            return -1
        
        task_id = self._next_task_id
        self._next_task_id += 1
        
        task = ScheduledTask(task_id, leds, start_time, duration, brightness, restore_original)
        self._scheduled_tasks.append(task)
        task.schedule()
        
        logger.debug(f"Scheduled task {task_id} for LEDs {led_ids}: start={start_time}, duration={duration}, brightness={brightness}")
        return task_id
    
    def schedule_led(self, led_id: int, start_time: int, duration: int, brightness: int = 100, restore_original: bool = True) -> int:
        """
        Schedule a single LED to turn on at a specific time for a specific duration
        
        Args:
            led_id: ID of the LED to schedule
            start_time: Time to turn on (in time units from now)
            duration: How long to stay on (in time units)
            brightness: Brightness level (0-100)
            restore_original: Whether to restore original brightness after task completes
            
        Returns:
            task_id: ID of the scheduled task
        """
        return self.schedule_leds([led_id], start_time, duration, brightness, restore_original)
    
    def schedule_row(self, row: int, start_time: int, duration: int, brightness: int = 100, restore_original: bool = True) -> int:
        """
        Schedule all LEDs in a row to turn on at a specific time for a specific duration
        
        Args:
            row: Row index (0-based)
            start_time: Time to turn on (in time units from now)
            duration: How long to stay on (in time units)
            brightness: Brightness level (0-100)
            restore_original: Whether to restore original brightness after task completes
            
        Returns:
            task_id: ID of the scheduled task
        """
        if not (0 <= row < self.rows):
            logger.error(f"Row {row} is out of bounds")
            return -1
        
        led_ids = [row * self.cols + col for col in range(self.cols)]
        return self.schedule_leds(led_ids, start_time, duration, brightness, restore_original)
    
    def schedule_column(self, col: int, start_time: int, duration: int, brightness: int = 100, restore_original: bool = True) -> int:
        """
        Schedule all LEDs in a column to turn on at a specific time for a specific duration
        
        Args:
            col: Column index (0-based)
            start_time: Time to turn on (in time units from now)
            duration: How long to stay on (in time units)
            brightness: Brightness level (0-100)
            restore_original: Whether to restore original brightness after task completes
            
        Returns:
            task_id: ID of the scheduled task
        """
        if not (0 <= col < self.cols):
            logger.error(f"Column {col} is out of bounds")
            return -1
        
        led_ids = [row * self.cols + col for row in range(self.rows)]
        return self.schedule_leds(led_ids, start_time, duration, brightness, restore_original)
    
    def schedule_all(self, start_time: int, duration: int, brightness: int = 100, restore_original: bool = True) -> int:
        """
        Schedule all LEDs to turn on at a specific time for a specific duration
        
        Args:
            start_time: Time to turn on (in time units from now)
            duration: How long to stay on (in time units)
            brightness: Brightness level (0-100)
            restore_original: Whether to restore original brightness after task completes
            
        Returns:
            task_id: ID of the scheduled task
        """
        led_ids = list(range(len(self.leds)))
        return self.schedule_leds(led_ids, start_time, duration, brightness, restore_original)
    
    def schedule_pattern(self, pattern: List[List[int]], start_time: int, duration: int, restore_original: bool = True) -> List[int]:
        """
        Schedule a pattern of brightness values to appear at a specific time for a specific duration
        
        Args:
            pattern: 2D list of brightness values (0-100)
            start_time: Time to turn on (in time units from now)
            duration: How long to stay on (in time units)
            restore_original: Whether to restore original brightness after task completes
            
        Returns:
            List of task IDs
        """
        task_ids = []
        
        # Group LEDs by brightness value to minimize the number of tasks
        brightness_groups = {}
        
        for row in range(min(len(pattern), self.rows)):
            for col in range(min(len(pattern[row]), self.cols)):
                brightness = pattern[row][col]
                if brightness > 0:  # Only schedule LEDs that need to be on
                    led_id = row * self.cols + col
                    if brightness not in brightness_groups:
                        brightness_groups[brightness] = []
                    brightness_groups[brightness].append(led_id)
        
        # Create a task for each brightness group
        for brightness, led_ids in brightness_groups.items():
            task_id = self.schedule_leds(led_ids, start_time, duration, brightness, restore_original)
            task_ids.append(task_id)
        
        return task_ids
    
    def cancel_task(self, task_id: int) -> bool:
        """
        Cancel a scheduled task if it hasn't executed yet
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            Success: True if task was cancelled, False otherwise
        """
        for task in self._scheduled_tasks:
            if task.task_id == task_id:
                return task.cancel()
        
        logger.error(f"Task {task_id} not found")
        return False
    
    def get_scheduled_task_count(self) -> int:
        """Return number of tasks scheduled"""
        # Count tasks that haven't been executed yet
        return sum(1 for task in self._scheduled_tasks if not task.executed)
    
    def __str__(self) -> str:
        return f"LEDMatrix({self.rows}x{self.cols}, {len(self.leds)} LEDs)"


class LEDManager:
    """A simple LED manager that provides basic LED control functionality"""
    
    def __init__(self, hardware):
        """
        Initialize the LED manager
        
        Args:
            hardware: Hardware controller object (PCA9685 or mock)
        """
        self.hardware = hardware
        self.leds = {}  # Dictionary to store LED objects by ID
        self._next_led_id = 0
        
    @property
    def num_leds(self) -> int:
        """Get the number of LEDs being managed"""
        return len(self.leds)
    
    def set_led(self, led_id: int, brightness: float):
        """
        Set the brightness of an LED
        
        Args:
            led_id: ID of the LED to control
            brightness: Brightness level from 0.0 (off) to 1.0 (full brightness)
        """
        # Clamp brightness between 0 and 1
        brightness = max(0.0, min(1.0, brightness))
        
        # Convert to 0-100 scale for LED class
        brightness_percent = int(brightness * 100)
        
        # Get or create LED object
        if led_id not in self.leds:
            self.leds[led_id] = LED(led_id, self.hardware, led_id % 16)
        
        # Set brightness
        self.leds[led_id].brightness = brightness_percent
    
    def get_led_state(self, led_id: int) -> float:
        """
        Get the current brightness of an LED
        
        Args:
            led_id: ID of the LED to check
            
        Returns:
            Current brightness level from 0.0 to 1.0
        """
        if led_id not in self.leds:
            return 0.0
        
        # Convert from 0-100 scale back to 0-1
        return self.leds[led_id].brightness / 100.0
    
    def all_off(self):
        """Turn all LEDs off"""
        for led in self.leds.values():
            led.off()
    
    def all_on(self, brightness: float = 1.0):
        """Turn all LEDs on at specified brightness"""
        for led in self.leds.values():
            self.set_led(led.led_id, brightness)