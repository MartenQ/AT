import random
import time
import inspect

class NaturalBehavior:
    """Kapselt das natürliche Verhalten des Roboters."""

    def __init__(self, robot):
        self.robot = robot
        self.last_idle_action = 0
        self.idle_action_interval = (10, 25)  # zufällige Pause

        # Alle Methoden, die mit "_action_" beginnen, automatisch als Idle-Funktion registrieren
        self.idle_functions = [
            method for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name.startswith("_action_")
        ]

    def touch(self):
        """Wird aufgerufen, wenn der Roboter aktiv wird."""
        self.robot.last_activity = time.time()

    def idle_action(self):
        if not self.idle_functions:
            return
        random.choice(self.idle_functions)()

    # --- Idle Aktionen ---
    def _action_look_around(self):
        texts = ["uh...", "Was ist das.", "Guck mal da.","soso...", "Interessant."," hm...","Ach so.","Oh!", "Aha!"]
        direction1, direction2 = (self.robot.left, self.robot.right) if random.choice([True, False]) else (self.robot.right, self.robot.left)
        self.robot.stop()
        direction1(); time.sleep(0.4); self.robot.stop(); time.sleep(0.2)
        direction2(); time.sleep(0.8); self.robot.stop(); direction1(); time.sleep(0.4); self.robot.stop()
        self.robot.eyes.stop_animation()
        time.sleep(random.randint(1, 100) / 100)
        self.robot.say(random.choice(texts))

    def _action_eye_color(self):
        colors = ["#00ffcc", "#ff00ff", "#ffaa00", "#00aaff", "#ff0000", "#00ff00", "#0000ff"]
        self.robot.eyes.set_color_hex(random.choice(colors))

    def _action_sound(self):
        direction1, direction2 = (self.robot.left, self.robot.right) if random.choice([True, False]) else (self.robot.right, self.robot.left)
        self.robot.stop()
        direction1(); time.sleep(0.4); self.robot.stop(); time.sleep(0.2)
        direction2(); time.sleep(0.8); self.robot.stop()
        self.robot.play_random_file("/home/at/AT/audio/beep")
        time.sleep(0.2); direction1(); time.sleep(0.4); self.robot.stop()

    def _action_say(self):
        texts = ["hm...", "Ich bin noch da.", "Langweilig hier.", "Hallo?"]
        self.robot.back(); time.sleep(0.4); self.robot.stop()
        self.robot.say(random.choice(texts))
        self.robot.fwd(); time.sleep(0.4); self.robot.stop()

    def check_idle(self):
        now = time.time()
        idle_time = now - self.robot.last_activity
        if idle_time > self.robot.idle_cooldown:
            if now - self.last_idle_action > random.randint(*self.idle_action_interval):
                self.last_idle_action = now
                self.idle_action()
