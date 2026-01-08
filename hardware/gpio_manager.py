# hardware/gpio_manager.py

import RPi.GPIO as GPIO

class GPIOManager:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def setup_output(self, pin):
        GPIO.setup(pin, GPIO.OUT)

    def pwm(self, pin, frequency):
        return GPIO.PWM(pin, frequency)

    def cleanup(self):
        GPIO.cleanup()
