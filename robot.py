from hardware.gpio_manager import GPIOManager
from hardware.motor import Motor
from control.movement import MovementController
from hardware.eyes import Eyes
from audio.tts import OfflineTextToSpeech
from audio.stt import OfflineSpeechToText
from control.tracker import Tracker
import config.config as config
import os
import random
import time
import threading
import cv2
from picamera2 import Picamera2
import numpy as np
import board
import busio
import adafruit_vl53l0x


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

        # Abstandssensor initialisieren
        i2c = busio.I2C(board.SCL, board.SDA)
        self.range_sensor = adafruit_vl53l0x.VL53L0X(i2c)

        # Abstandsschwellen aus config
        self.min_distance = config.VL53L0X_MIN_DISTANCE
        self.slow_distance = config.VL53L0X_SLOW_DISTANCE


    # --- Motorsteuerung ---
    def fwd(self): self.movement.forward()
    def back(self): self.movement.backward()
    def left(self): self.movement.left()
    def right(self): self.movement.right()
    def stop(self): self.movement.stop()

    def adaptive_forward(self):
        self.distance_thread_running = True

        while self.distance_thread_running:
            distance = self.range_sensor.range  # Abstand in mm
            print(f"Abstand: {distance} mm")

            if distance < self.min_distance * 10:  # zu nah → stop & nur rückwärts/links/rechts
                self.stop()
                print("Zu nah! Stoppe.")
            elif distance < self.slow_distance * 10:
                # Geschwindigkeit anpassen
                factor = (distance / (self.slow_distance * 10))  # 0–1
                speed = int(config.DEFAULT_SPEED * factor)
                self.movement.left_motor.set_speed(speed)
                self.movement.right_motor.set_speed(speed)
                print(f"Langsamer fahren: Geschwindigkeit {speed}")
            else:
                # normal vorwärts
                self.fwd()

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

    def follow_object_color(self, color="red"):
        """Starte Tracker für Objekt/Farbe"""
        self.say(f"Ich folge dem {color}en Objekt")
        self.tracker = Tracker(self, color=color)
        self.tracker.start()

    def follow_person(self, color="red"):
        """Starte Tracker für Person (Farberkennung, z.B. Kleidung)"""
        self.say("Ich folge der Person")
        self.tracker = Tracker(self, color=color)
        self.tracker.start()

    def stop_following(self):
        if hasattr(self, "tracker") and self.tracker:
            self.tracker.stop()
            self.distance_thread_running = False


    # --- Shutdown ---
    def shutdown(self):
        self.movement.stop()
        self.gpio.cleanup()