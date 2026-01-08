from hardware.gpio_manager import GPIOManager
from hardware.motor import Motor
from control.movement import MovementController
from hardware.eyes import Eyes
from audio.tts import OfflineTextToSpeech
from audio.stt import OfflineSpeechToText
import config
import os
import random
import time
import threading
from picamera2 import Picamera2
import numpy as np

from control.behavior import NaturalBehavior  # <--- Import der neuen Klasse


class Robot:
    def __init__(self):
        self.gpio = GPIOManager()

        # Motor-Pins
        pins = [
            config.LEFT_MOTOR_FORWARD,
            config.LEFT_MOTOR_BACKWARD,
            config.RIGHT_MOTOR_FORWARD,
            config.RIGHT_MOTOR_BACKWARD
        ]
        for pin in pins:
            self.gpio.setup_output(pin)

        left_motor = Motor(
            self.gpio.pwm(config.LEFT_MOTOR_FORWARD, config.PWM_FREQUENCY),
            self.gpio.pwm(config.LEFT_MOTOR_BACKWARD, config.PWM_FREQUENCY)
        )
        right_motor = Motor(
            self.gpio.pwm(config.RIGHT_MOTOR_FORWARD, config.PWM_FREQUENCY),
            self.gpio.pwm(config.RIGHT_MOTOR_BACKWARD, config.PWM_FREQUENCY)
        )

        self.movement = MovementController(left_motor, right_motor, config.DEFAULT_SPEED)

        # Audio & Eyes
        self.wake_words = ["roboter", "robot", "boter", "ter", "robo", "rob", "bot", "potter", "pott"]
        self.tts = OfflineTextToSpeech()
        self.stt = OfflineSpeechToText(wake_words=self.wake_words)
        self.eyes = Eyes()

        self.last_activity = time.time()
        self.idle_cooldown = 15  # Sekunden bis erste Idle-Aktion

        # --- Natürliches Verhalten ---
        self.natural_behavior = NaturalBehavior(self)

    # --- Motorsteuerung ---
    def fwd(self): self.movement.forward()
    def back(self): self.movement.backward()
    def left(self): self.movement.left()
    def right(self): self.movement.right()
    def stop(self): self.movement.stop()

    # --- Audio ---
    def say(self, text: str):
        self.tts.speak(text)

    def mp3(self, path: str):
        self.tts.play(path)

    def play_random_file(self, folder_path: str):
        if not os.path.isdir(folder_path):
            print(f"⚠️ Ordner nicht gefunden: {folder_path}")
            return
        files = [f for f in os.listdir(folder_path) if f.lower().endswith((".mp3", ".wav"))]
        if not files:
            print(f"⚠️ Keine Audiodateien im Ordner: {folder_path}")
            return
        file_to_play = random.choice(files)
        self.tts.play(os.path.join(folder_path, file_to_play))

    # --- Sprachsteuerung ---
    def listen_for_wake_word_and_command(self):
        wake_detected, command = self.stt.listen_once()
        if wake_detected:
            return command
        return None

    # --- Idle check ---
    def check_idle(self):
        self.natural_behavior.check_idle()

    # --- Shutdown ---
    def shutdown(self):
        self.movement.stop()
        self.gpio.cleanup()

    def follow_object(self, color="red"):
        """
        Objekt verfolgen mit Picamera2. Läuft in einem eigenen Thread, bis stop_following() aufgerufen wird.
        """
        self._following = True

        def _follow():
            picam2 = Picamera2()
            preview_config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
            picam2.configure(preview_config)
            picam2.start()

            try:
                while self._following:
                    frame = picam2.capture_array()
                    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

                    if color == "red":
                        lower_red1 = np.array([0, 120, 70])
                        upper_red1 = np.array([10, 255, 255])
                        lower_red2 = np.array([170, 120, 70])
                        upper_red2 = np.array([180, 255, 255])
                        mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
                    else:
                        mask = cv2.inRange(hsv, np.array([0,0,0]), np.array([0,0,0]))

                    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    if contours:
                        c = max(contours, key=cv2.contourArea)
                        x, y, w, h = cv2.boundingRect(c)
                        cx = x + w // 2
                        frame_center = frame.shape[1] // 2

                        if cx < frame_center - 30:
                            self.left()
                        elif cx > frame_center + 30:
                            self.right()
                        else:
                            self.fwd()
                    else:
                        self.stop()

                    time.sleep(0.05)
            finally:
                picam2.stop()
                self.stop()

        threading.Thread(target=_follow, daemon=True).start()

    def stop_following(self):
        """Stoppt die Objektverfolgung"""
        self._following = False
        self.stop()
