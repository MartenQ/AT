import random
import time

class NaturalBehavior:
    """Kapselt das natürliche Verhalten des Roboters."""

    def __init__(self, robot):
        self.robot = robot
        self.last_idle_action = 0
        self.idle_action_interval = (10, 25)  # zufällige Pause

    def touch(self):
        """Wird aufgerufen, wenn der Roboter aktiv wird."""
        self.robot.last_activity = time.time()

    def idle_action(self):
        actions = [
            self._look_around,
            self._eye_color,
            self._sound,
            self._say
        ]
        random.choice(actions)()

    # --- Idle Aktionen ---
    def _look_around(self):
        texts = ["Hmm?", "Was ist das.", "Guck mal da.", "AHA"]
        # Richtung zufällig wählen
        if random.choice([True, False]):
            direction1 = self.robot.left
            direction2 = self.robot.right
        else:
            direction1 = self.robot.right
            direction2 = self.robot.left

        self.robot.stop()
        direction1()
        time.sleep(0.4)
        self.robot.stop()
        time.sleep(0.2)
        direction2()
        time.sleep(0.8)
        self.robot.stop()
        direction1()
        time.sleep(0.4)
        self.robot.stop()

        self.robot.eyes.stop_animation()
        time.sleep(random.randint(1, 100) / 100)
        self.robot.say(random.choice(texts))

    def _eye_color(self):
        colors = ["#00ffcc", "#ff00ff", "#ffaa00", "#00aaff", "#ff0000", "#00ff00", "#0000ff"]
        self.robot.eyes.set_color_hex(random.choice(colors))

    def _sound(self):
        # Richtung zufällig wählen
        if random.choice([True, False]):
            direction1 = self.robot.left
            direction2 = self.robot.right
        else:
            direction1 = self.robot.right
            direction2 = self.robot.left

        self.robot.stop()
        direction1()
        time.sleep(0.4)
        self.robot.stop()
        time.sleep(0.2)
        direction2()
        time.sleep(0.8)
        self.robot.stop()
        self.robot.play_random_file("/home/at/AT/audio/beep")
        time.sleep(0.2)
        direction1()
        time.sleep(0.4)
        self.robot.stop()

    def _say(self):
        texts = ["Hmm?", "Ich bin noch da.", "Langweilig hier.", "Hallo?"]
        self.robot.back()
        time.sleep(0.4)
        self.robot.stop()
        self.robot.say(random.choice(texts))
        self.robot.fwd()
        time.sleep(0.4)
        self.robot.stop()

    def check_idle(self):
        now = time.time()
        idle_time = now - self.robot.last_activity

        if idle_time > self.robot.idle_cooldown:
            if now - self.last_idle_action > random.randint(*self.idle_action_interval):
                self.last_idle_action = now
                self.idle_action()
