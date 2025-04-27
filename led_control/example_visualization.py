from led_management import LEDMatrix
from led_visualizer import LEDVisualizer
import time
import threading

def main():
    # Create a 4x4 LED matrix (without real hardware controllers)
    matrix = LEDMatrix(4, 4)
    
    # Create and start the visualizer
    visualizer = LEDVisualizer(matrix)
    
    # Create a demo pattern in a separate thread
    def demo_pattern():
        while True:
            # Turn on each LED in sequence
            for row in range(matrix.rows):
                for col in range(matrix.cols):
                    led = matrix.led_at(row, col)
                    if led:
                        led.on(100)  # Full brightness
                        time.sleep(0.5)  # Wait half a second
                        led.off()
    
    # Start the demo pattern in a background thread
    pattern_thread = threading.Thread(target=demo_pattern, daemon=True)
    pattern_thread.start()
    
    # Run the visualizer (this will block until window is closed)
    visualizer.run()

if __name__ == "__main__":
    main() 