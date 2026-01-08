# hardware/eyes.py

import threading
import time
import math
import RPi.GPIO as GPIO
import config


class Eyes:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.base_color = {"rot": 0.0, "gelb": 0.0, "blau": 0.0}
        self.running = False
        self.thread = None

        self.pwm = {}
        for color, pin in config.EYE_PINS.items():
            GPIO.setup(pin, GPIO.OUT)
            pwm = GPIO.PWM(pin, config.EYE_PWM_FREQ)
            pwm.start(100)  # invertiert → AUS
            self.pwm[color] = pwm

    # -----------------------------
    # Öffentliche API
    # -----------------------------

    def set_color_rgb(self, r: int, g: int, b: int):
        self._set_base_color(r, g, b)

    def set_color_hex(self, hex_code: str):
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        self.set_color_rgb(r, g, b)

    def off(self):
        self.stop_animation()
        self._apply_brightness(0)

    def breathe(self):
        self.stop_animation()
        self.running = True
        self.thread = threading.Thread(
            target=self._breathe_loop,
            daemon=True
        )
        self.thread.start()

    def stop_animation(self):
        self.running = False
        self._apply_brightness(100)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.1)
        

    # -----------------------------
    # Intern
    # -----------------------------

    def _set_base_color(self, r, g, b):
        min_val = (config.EYE_SUPPLY_V - config.EYE_MAX_VLED) \
                  / config.EYE_SUPPLY_V * 255

        r = max(r, min_val)
        g = max(g, min_val)
        b = max(b, min_val)

        self.base_color["rot"] = r / 255 * 100
        self.base_color["gelb"] = g / 255 * 100
        self.base_color["blau"] = b / 255 * 100

    def _apply_brightness(self, brightness):
        for color, pwm in self.pwm.items():
            base = self.base_color[color]
            if base <= 0:
                pwm.ChangeDutyCycle(100)
            else:
                duty = 100 - (base * brightness)
                pwm.ChangeDutyCycle(max(0, min(100, duty)))

    def _breathe_loop(self):
        steps = config.EYE_BREATHE_STEPS
        delay = 1 / (config.EYE_BREATHE_FREQ * steps)

        while self.running:
            for i in range(steps):
                if not self.running:
                    break
                phase = 2 * math.pi * i / steps
                brightness = (math.sin(phase) + 1) / 2
                self._apply_brightness(brightness)
                time.sleep(delay)
