from robot import Robot
import config.config as config
from audio.stt import OfflineSpeechToText

robot = Robot()

# Befehle
COMMAND_ACTIONS = {
    "forward": lambda r: (r.fwd(), r.say("Ich fahre los")),
    "backward": lambda r: (r.back(), r.say("Ich fahre zurück")),
    "left": lambda r: (r.left(), r.say("Ich fahre links")),
    "right": lambda r: (r.right(), r.say("Ich fahre rechts")),
    "stop": lambda r: (r.stop(), r.say("Ich stoppe")),
    "motivation": lambda r: r.say("Los Alina, los los Alina"),
    "follow_object": lambda r: r.follow_object_color(color="red"),
    "follow_person": lambda r: r.follow_person(color="red"),
    "stop_follow": lambda r: (r.say("Ich höre auf zu folgen"), r.stop_following()),
    "entchen": lambda r: (
        r.say("Jetzt spiele ich Alle meine Entchen"),
        r.mp3("audio/instrumental/alle_meine_entchen.mp3")
    ),
}

# Augenanimation starten
robot.eyes.set_color_hex("#00ffcc")
robot.eyes.breathe()

# STT initialisieren
stt = OfflineSpeechToText(
    wake_words=["roboter"],
    model_path="models/vosk-model-small-de-0.15"
)

try:
    while True:
        robot.check_idle()
        robot.eyes.breathe()

        # --- Wake-Word + Kommando ---
        detected_wake_word, command = stt.listen_for_wake_word_and_command(
            wake_window=5,   # ≥5 Sekunden für zuverlässige Wake-Word-Erkennung
            overlap=1        # Überlappung, schnelle Reaktion
        )

        if not detected_wake_word:
            continue  # kein Wake-Word erkannt

        robot.eyes.stop_animation()
        robot.play_random_file("/home/at/AT/audio/beep")
        robot.say(f"Du hast gesagt: {command}")

        handled = False
        for cmd_name, keywords in config.COMMAND_KEYWORDS.items():
            for word in keywords:
                if word in command:
                    # Spezieller Fall: "folge" → unterscheiden zwischen Objekt und Person
                    if cmd_name == "follow":
                        if any(k in command for k in ["person", "menschen", "alina"]):
                            robot.follow_person(color="green")
                        else:
                            robot.follow_object_color(color="red")
                    else:
                        action = COMMAND_ACTIONS.get(cmd_name)
                        if action:
                            action(robot)
                    handled = True
                    break
            if handled:
                break

        if not handled:
            robot.say("Das kenne ich nicht")

except KeyboardInterrupt:
    robot.say("Notaus")

finally:
    robot.shutdown()
