# main.py                                                                main.py                                                                            
from robot import Robot
import config

robot = Robot()

COMMAND_ACTIONS = {
    "forward": lambda r: (r.fwd(), r.say("Ich fahre los")),
    "backward": lambda r: (r.back(), r.say("Ich fahre zurück")),
    "left": lambda r: (r.left(), r.say("Ich fahre links")),
    "right": lambda r: (r.right(), r.say("Ich fahre rechts")),
    "stop": lambda r: (r.stop(), r.say("Ich stoppe")),
    "motivation": lambda r: r.say("Los Alina, los los Alina"),
    "entchen": lambda r: (
        r.say("Jetzt spiele ich Alle meine Entchen"),
        r.mp3("audio/instrumental/alle_meine_entchen.mp3")
    ),
}


try:
    while True:
        robot.check_idle()

        # Augenanimation starten
        robot.eyes.breathe()
        robot.eyes.set_color_hex("#00ffcc")

        # Wake-Word + Kommando
        command = robot.listen_for_wake_word_and_command()
        if not command:
            continue  # kein Wake-Word erkannt
        robot.touch()   # 👈 SEHR wichtig

        robot.eyes.stop_animation()
        robot.eyes.set_color_hex("#0000FF")
        robot.eyes.breathe()
        robot.play_random_file("/home/at/AT/audio/beep")

        robot.say(f"Du hast gesagt {command}")

        handled = False

        for cmd_name, keywords in config.COMMAND_KEYWORDS.items():
            for word in keywords:
                if word in command:
                    robot.touch()
                    action = COMMAND_ACTIONS.get(cmd_name)
                    if action:
                        action(robot)
                    handled = True
                    break
            if handled:
                break

        if not handled:
            robot.say("Das kenne ich nicht")


        robot.eyes.set_color_hex("#00ffcc")

except KeyboardInterrupt:
    robot.say("Notaus")

finally:
    robot.shutdown()


