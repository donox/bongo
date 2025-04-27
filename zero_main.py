from adafruit_pca9685 import PCA9685
import busio
import board
import sys
import time
from gpiozero import LED
from time import sleep

if __name__=="__main__":

    # Use the onboard LED
    led = LED("led0")  # This refers to the built-in ACT LED

    # Blink 10 times
    for i in range(10):
        led.on()
        print(f"Blink {i+1} of 10 - ON")
        sleep(0.5)
        led.off()
        print(f"Blink {i+1} of 10 - OFF")
        sleep(0.5)

print("LED blinking complete")