from typing import List, Optional, Dict, Any
from .led_management import LEDMatrix
import time
from ..logging_setup import logger
from ..constants import TIME_UNIT


class LightingPattern:
    """Class to define and manage lighting patterns for the LED matrix"""
    
    def __init__(self, matrix: LEDMatrix, name: str = "unnamed_pattern"):
        """
        Initialize a lighting pattern
        
        Args:
            matrix: The LEDMatrix instance to control
            name: Name of the pattern for identification
        """
        self.matrix = matrix
        self.name = name
        self.pattern_sequence: List[Dict[str, Any]] = []
        
    def add_step(self, pattern: List[List[int]], duration: int, transition_time: int = 0):
        """
        Add a step to the pattern sequence
        
        Args:
            pattern: 2D list of brightness values (0-100) matching matrix dimensions
            duration: How long to display this pattern (in time units)
            transition_time: Time to transition from previous pattern (in time units)
        """
        if len(pattern) != self.matrix.rows or any(len(row) != self.matrix.cols for row in pattern):
            raise ValueError(f"Pattern dimensions must match matrix dimensions ({self.matrix.rows}x{self.matrix.cols})")
        
        self.pattern_sequence.append({
            "pattern": pattern,
            "duration": duration,
            "transition_time": transition_time
        })
        logger.debug(f"Added step to pattern '{self.name}' with duration {duration}")
    
    def add_row_step(self, row: int, brightness: int, duration: int, transition_time: int = 0):
        """Add a step that lights up a specific row"""
        pattern = [[0] * self.matrix.cols for _ in range(self.matrix.rows)]
        pattern[row] = [brightness] * self.matrix.cols
        self.add_step(pattern, duration, transition_time)
        
    def add_column_step(self, col: int, brightness: int, duration: int, transition_time: int = 0):
        """Add a step that lights up a specific column"""
        pattern = [[0] * self.matrix.cols for _ in range(self.matrix.rows)]
        for row in range(self.matrix.rows):
            pattern[row][col] = brightness
        self.add_step(pattern, duration, transition_time)
    
    def clear_sequence(self):
        """Clear all steps in the pattern sequence"""
        self.pattern_sequence = []
        logger.debug(f"Cleared pattern sequence for '{self.name}'")
    
    def run_once(self, start_delay: int = 0) -> List[int]:
        """
        Run the pattern sequence once
        
        Args:
            start_delay: Delay before starting the pattern (in time units)
            
        Returns:
            List of task IDs created
        """
        if not self.pattern_sequence:
            logger.warning(f"No steps in pattern '{self.name}'")
            return []
        
        task_ids = []
        current_time = start_delay
        
        for step in self.pattern_sequence:
            # Schedule the pattern
            task_ids.extend(
                self.matrix.schedule_pattern(
                    step["pattern"],
                    current_time,
                    step["duration"],
                    restore_original=True
                )
            )
            current_time += step["duration"] + step["transition_time"]
        
        logger.info(f"Scheduled pattern '{self.name}' with {len(self.pattern_sequence)} steps")
        return task_ids
    
    def run_loop(self, repetitions: int, start_delay: int = 0) -> List[int]:
        """
        Run the pattern sequence multiple times
        
        Args:
            repetitions: Number of times to repeat the pattern
            start_delay: Delay before starting the pattern (in time units)
            
        Returns:
            List of all task IDs created
        """
        all_task_ids = []
        total_duration = sum(step["duration"] + step["transition_time"] for step in self.pattern_sequence)
        
        for i in range(repetitions):
            current_delay = start_delay + (i * total_duration)
            all_task_ids.extend(self.run_once(current_delay))
        
        return all_task_ids
    
    def stop(self, task_ids: List[int]):
        """
        Stop a running pattern by canceling its tasks
        
        Args:
            task_ids: List of task IDs to cancel
        """
        for task_id in task_ids:
            self.matrix.cancel_task(task_id)
        logger.info(f"Stopped pattern '{self.name}'")

    def add_chase_pattern(self, brightness: int = 100, direction: str = "right", duration_per_step: int = 5):
        """
        Add a chase pattern that moves across the matrix
        
        Args:
            brightness: Brightness level (0-100)
            direction: One of "right", "left", "up", "down"
            duration_per_step: How long each step should last
        """
        if direction in ["right", "left"]:
            for col in range(self.matrix.cols):
                col_idx = col if direction == "right" else (self.matrix.cols - 1 - col)
                self.add_column_step(col_idx, brightness, duration_per_step)
        else:  # up or down
            for row in range(self.matrix.rows):
                row_idx = row if direction == "down" else (self.matrix.rows - 1 - row)
                self.add_row_step(row_idx, brightness, duration_per_step)
    
    def add_wave_pattern(self, brightness: int = 100, direction: str = "right", width: int = 2, duration_per_step: int = 5):
        """
        Add a wave pattern that moves across the matrix with a wider light band
        
        Args:
            brightness: Brightness level (0-100)
            direction: One of "right", "left", "up", "down"
            width: Width of the wave in LEDs
            duration_per_step: How long each step should last
        """
        if direction in ["right", "left"]:
            for col in range(-width + 1, self.matrix.cols):
                pattern = [[0] * self.matrix.cols for _ in range(self.matrix.rows)]
                for w in range(width):
                    curr_col = col + w
                    if 0 <= curr_col < self.matrix.cols:
                        for row in range(self.matrix.rows):
                            col_idx = curr_col if direction == "right" else (self.matrix.cols - 1 - curr_col)
                            pattern[row][col_idx] = brightness
                self.add_step(pattern, duration_per_step)
        else:  # up or down
            for row in range(-width + 1, self.matrix.rows):
                pattern = [[0] * self.matrix.cols for _ in range(self.matrix.rows)]
                for w in range(width):
                    curr_row = row + w
                    if 0 <= curr_row < self.matrix.rows:
                        row_idx = curr_row if direction == "down" else (self.matrix.rows - 1 - curr_row)
                        pattern[row_idx] = [brightness] * self.matrix.cols
                self.add_step(pattern, duration_per_step)
    
    def add_pulse_pattern(self, max_brightness: int = 100, min_brightness: int = 0, steps: int = 10, duration_per_step: int = 2):
        """
        Add a pulsing pattern that fades all LEDs up and down
        
        Args:
            max_brightness: Maximum brightness level (0-100)
            min_brightness: Minimum brightness level (0-100)
            steps: Number of steps in fade up/down
            duration_per_step: How long each step should last
        """
        # Fade up
        for i in range(steps):
            brightness = min_brightness + ((max_brightness - min_brightness) * i // (steps - 1))
            pattern = [[brightness] * self.matrix.cols for _ in range(self.matrix.rows)]
            self.add_step(pattern, duration_per_step)
        
        # Fade down
        for i in range(steps):
            brightness = max_brightness - ((max_brightness - min_brightness) * i // (steps - 1))
            pattern = [[brightness] * self.matrix.cols for _ in range(self.matrix.rows)]
            self.add_step(pattern, duration_per_step)
    
    def add_spiral_pattern(self, brightness: int = 100, clockwise: bool = True, duration_per_step: int = 3):
        """
        Add a spiral pattern that moves from the outside to the center
        
        Args:
            brightness: Brightness level (0-100)
            clockwise: Direction of spiral
            duration_per_step: How long each step should last
        """
        def get_spiral_coordinates():
            coordinates = []
            top, bottom = 0, self.matrix.rows - 1
            left, right = 0, self.matrix.cols - 1
            
            while top <= bottom and left <= right:
                # Top row
                for i in range(left, right + 1):
                    coordinates.append((top, i))
                top += 1
                
                # Right column
                for i in range(top, bottom + 1):
                    coordinates.append((i, right))
                right -= 1
                
                if top <= bottom:
                    # Bottom row
                    for i in range(right, left - 1, -1):
                        coordinates.append((bottom, i))
                    bottom -= 1
                
                if left <= right:
                    # Left column
                    for i in range(bottom, top - 1, -1):
                        coordinates.append((i, left))
                    left += 1
            
            return coordinates if clockwise else coordinates[::-1]
        
        coordinates = get_spiral_coordinates()
        for row, col in coordinates:
            pattern = [[0] * self.matrix.cols for _ in range(self.matrix.rows)]
            pattern[row][col] = brightness
            self.add_step(pattern, duration_per_step)
    
    def add_random_sparkle(self, max_active: int = 3, brightness: int = 100, steps: int = 20, duration_per_step: int = 2):
        """
        Add a random sparkling pattern
        
        Args:
            max_active: Maximum number of LEDs lit at once
            brightness: Brightness level (0-100)
            steps: Number of random patterns to generate
            duration_per_step: How long each step should last
        """
        from random import sample
        total_leds = self.matrix.rows * self.matrix.cols
        
        for _ in range(steps):
            pattern = [[0] * self.matrix.cols for _ in range(self.matrix.rows)]
            # Pick random LEDs to light up
            active_leds = sample(range(total_leds), min(max_active, total_leds))
            
            for led_idx in active_leds:
                row = led_idx // self.matrix.cols
                col = led_idx % self.matrix.cols
                pattern[row][col] = brightness
            
            self.add_step(pattern, duration_per_step) 