# config.py

import json
import os

# GPIO Pins (BCM Nummerierung)
LEFT_MOTOR_FORWARD = 24
LEFT_MOTOR_BACKWARD = 22

RIGHT_MOTOR_FORWARD = 23
RIGHT_MOTOR_BACKWARD = 25

PWM_FREQUENCY = 1000
DEFAULT_SPEED = 100  # 0–100

# Abstandssensor VL53L0X
VL53L0X_MIN_DISTANCE = 15    # cm → stoppt wenn näher
VL53L0X_SLOW_DISTANCE = 40   # cm → verlangsamen ab diesem Abstand



# Audio
TTS_LANGUAGE = "de"
TTS_VOLUME = 1.2
TTS_TMP_MP3 = "/tmp/tts_output.mp3"
TTS_TMP_WAV = "/tmp/tts_output.wav"
PLAY_TMP_WAV = "/tmp/play_output.wav"

max_record_seconds = 10 # Maximale Aufnahmezeit für STT in Sekunden


# Augen LEDs (BCM)
EYE_PINS = {
    "rot": 6,
    "gelb": 5,
    "blau": 4
}

EYE_PWM_FREQ = 1000  # Hz
EYE_MAX_VLED = 2.0
EYE_SUPPLY_V = 3.3

EYE_BREATHE_FREQ = 0.5
EYE_BREATHE_STEPS = 100

# -------------------------
# COMMAND_KEYWORDS aus JSON laden
# -------------------------
json_path = os.path.join(os.path.dirname(__file__), "command_keywords.json")

if os.path.isfile(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        COMMAND_KEYWORDS = json.load(f)
else:
    print(f"⚠️ command_keywords.json nicht gefunden unter {json_path}")
    COMMAND_KEYWORDS = {}