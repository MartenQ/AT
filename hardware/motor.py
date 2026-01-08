# hardware/motor.py

class Motor:
    def __init__(self, forward_pwm, backward_pwm):
        self.forward = forward_pwm
        self.backward = backward_pwm

        self.forward.start(0)
        self.backward.start(0)

    def set_speed(self, speed):
        speed = max(0, min(100, speed))
        self.forward.ChangeDutyCycle(speed)
        self.backward.ChangeDutyCycle(0)

    def reverse(self, speed):
        speed = max(0, min(100, speed))
        self.forward.ChangeDutyCycle(0)
        self.backward.ChangeDutyCycle(speed)

    def stop(self):
        self.forward.ChangeDutyCycle(0)
        self.backward.ChangeDutyCycle(0)
