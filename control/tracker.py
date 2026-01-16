# control/tracker.py

from picamera2 import Picamera2
import cv2
import numpy as np
import threading
import time

class Tracker:
    """
    Verfolgt ein Objekt oder eine Person basierend auf Farbe.
    Steuerung erfolgt über die Robot-Klasse.
    """

    COLOR_RANGES = {
        "red": [([0, 120, 70], [10, 255, 255]), ([170, 120, 70], [180, 255, 255])],
        "green": [([36, 25, 25], [86, 255, 255])],
        "blue": [([94, 80, 2], [126, 255, 255])]
    }

    def __init__(self, robot, color="red"):
        """
        robot: Instanz der Robot-Klasse
        color: Farbe des zu verfolgenden Objekts
        """
        self.robot = robot
        self.color = color
        self._tracking = False
        self._thread = None

    def start(self):
        """Starte die Verfolgung in einem eigenen Thread"""
        if self._tracking:
            return  # schon aktiv
        self._tracking = True
        self._thread = threading.Thread(target=self._track_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stoppe die Verfolgung"""
        self._tracking = False
        if self.robot:
            self.robot.stop()

    def _track_loop(self):
        picam2 = Picamera2()
        picam2.configure(
            picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
        )
        picam2.start()

        ranges = self.COLOR_RANGES.get(self.color, self.COLOR_RANGES["red"])

        try:
            while self._tracking:
                frame = picam2.capture_array()
                hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

                mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
                for lower, upper in ranges:
                    lower_np = np.array(lower)
                    upper_np = np.array(upper)
                    mask += cv2.inRange(hsv, lower_np, upper_np)

                # Konturen finden
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    # größtes Objekt
                    c = max(contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(c)
                    cx = x + w // 2
                    frame_center = frame.shape[1] // 2

                    # Bewegung steuern
                    if cx < frame_center - 40:
                        self.robot.left()
                    elif cx > frame_center + 40:
                        self.robot.right()
                    else:
                        self.robot.fwd()
                else:
                    self.robot.stop()

                time.sleep(0.1)
        finally:
            picam2.stop()
            self.robot.stop()
