# config.py

# GPIO Pins (BCM Nummerierung)
LEFT_MOTOR_FORWARD = 24
LEFT_MOTOR_BACKWARD = 22

RIGHT_MOTOR_FORWARD = 23
RIGHT_MOTOR_BACKWARD = 25

PWM_FREQUENCY = 1000
DEFAULT_SPEED = 100  # 0–100

# Audio
TTS_LANGUAGE = "de"
TTS_VOLUME = 1.2
TTS_TMP_MP3 = "/tmp/tts_output.mp3"
TTS_TMP_WAV = "/tmp/tts_output.wav"
PLAY_TMP_WAV = "/tmp/play_output.wav"


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

COMMAND_KEYWORDS = {
    "forward": ["fahr", "los", "vorwärts", "vorwaerts", "geh","vor"],
    "backward": ["zurück", "zurueck", "rückwärts", "rueckwaerts","zur"],
    "left": ["links", "linke","link","ks"],
    "right": ["rechts", "rechte","recht","ts"],
    "stop": ["stop", "stopp", "halt", "anhalten","top"],
    "motivation": ["motivation", "anfeuern"],
    "entchen": ["entchen", "lied","ent","ente"],
    "follow": ["folge", "verfolge", "tracke", "track"],
    "stop_follow": ["stopp folge", "hör auf zu folgen", "beende folgen"]
}
