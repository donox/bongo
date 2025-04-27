import tkinter as tk
from typing import Optional
from led_control.led_management import LEDMatrix, LED

class LEDVisualizer:
    """GUI visualization of an LED matrix"""
    
    def __init__(self, matrix: LEDMatrix, size: int = 30, padding: int = 5):
        """
        Initialize the LED matrix visualizer
        
        Args:
            matrix: The LED matrix to visualize
            size: Size of each LED circle in pixels
            padding: Padding between LEDs in pixels
        """
        self.matrix = matrix
        self.size = size
        self.padding = padding
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("LED Matrix Visualizer")
        
        # Calculate canvas size
        canvas_width = (size + padding) * matrix.cols + padding
        canvas_height = (size + padding) * matrix.rows + padding
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=canvas_width,
            height=canvas_height,
            bg='black'
        )
        self.canvas.pack()
        
        # Store circle IDs for each LED
        self.led_circles = {}
        
        # Create initial circles
        self._create_circles()
        
        # Set up periodic update
        self._update_display()
    
    def _create_circles(self):
        """Create circles for all LEDs"""
        for row in range(self.matrix.rows):
            for col in range(self.matrix.cols):
                x = (self.size + self.padding) * col + self.padding + self.size/2
                y = (self.size + self.padding) * row + self.padding + self.size/2
                
                led = self.matrix.led_at(row, col)
                if led:
                    circle = self.canvas.create_oval(
                        x - self.size/2, y - self.size/2,
                        x + self.size/2, y + self.size/2,
                        fill='red',  # Default color for off state
                        outline='darkgray'
                    )
                    self.led_circles[led.led_id] = circle
    
    def _update_display(self):
        """Update the display to reflect current LED states"""
        for led_id, circle in self.led_circles.items():
            led = self.matrix.leds[led_id]
            if led.is_on():
                # Calculate color based on brightness
                brightness_hex = hex(int(led.brightness * 255 / 100))[2:].zfill(2)
                color = f'#{brightness_hex}{brightness_hex}{brightness_hex}'
                self.canvas.itemconfig(circle, fill=color)
            else:
                self.canvas.itemconfig(circle, fill='red')
        
        # Schedule next update
        self.root.after(50, self._update_display)
    
    def run(self):
        """Start the visualization"""
        self.root.mainloop() 