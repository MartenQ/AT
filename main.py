# main.py                                                                main.py                                                                            
from robot import Robot
import config.config as config

robot = Robot()

COMMAND_ACTIONS = {
    "forward": lambda r: (r.fwd(), r.say("Ich fahre los")),
    "backward": lambda r: (r.back(), r.say("Ich fahre zurück")),
    "left": lambda r: (r.left(), r.say("Ich fahre links")),
    "right": lambda r: (r.right(), r.say("Ich fahre rechts")),
    "stop": lambda r: (r.stop(), r.say("Ich stoppe")),
    "motivation": lambda r: r.say("Los Marie, los los Marie, du schaffst das!"),

    # Neues: follow zwischen Objekt oder Person
    "follow_object": lambda r: r.follow_object_color(color="red"),  # Objekt (z.B. roter Ball)
    "follow_person": lambda r: r.follow_person(color="red"),        # Person (rote Kleidung)
    "stop_follow": lambda r: (r.say("Ich höre auf zu folgen"), r.stop_following()),

    "entchen": lambda r: (
        r.say("Jetzt spiele ich Alle meine Entchen"),
        r.mp3("audio/instrumental/alle_meine_entchen.mp3")
    ),
}


robot.eyes.set_color_hex("#00ffcc")
robot.eyes.breathe()

try:
    while True:
        robot.check_idle()

        # Augenanimation starten
        

        # --- Wake-Word + Kommando ---
        robot.eyes.breathe()
        command = robot.listen_for_wake_word_and_command()
        if not command:
            continue  # kein Wake-Word erkannt

        robot.eyes.stop_animation()
        # robot.eyes.set_color_hex("#0000FF")
        
        robot.play_random_file("/home/at/AT/audio/beep")

        robot.say(f"Du hast gesagt {command}")

        handled = False

        for cmd_name, keywords in config.COMMAND_KEYWORDS.items():
            for word in keywords:
                if word in command:
                    # Spezieller Fall: "folge" → unterscheiden zwischen Objekt und Person
                    if cmd_name == "follow":
                        if any(k in command for k in ["person", "menschen", "alina"]):  # Keywords für Person
                            robot.follow_person(color="green")  # z.B. grüne Kleidung
                        else:
                            robot.follow_object_color(color="red")  # z.B. roter Ball
                    else:
                        # Normale Commands
                        action = COMMAND_ACTIONS.get(cmd_name)
                        if action:
                            action(robot)
                    handled = True
                    break
            if handled:
                break

        if not handled:
            robot.say("Das kenne ich nicht")

        #robot.eyes.set_color_hex("#00ffcc")
#s

except KeyboardInterrupt:
    robot.say("Notaus")

finally:
    robot.shutdown()


